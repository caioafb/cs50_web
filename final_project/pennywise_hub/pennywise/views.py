from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator

from .models import User, Company, CompanyUser, Category, Account, Transaction, MonthlyAccountBalance

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        company_name = request.POST["company"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "pennywise/register.html", {
                "message": "Passwords must match."
            })

        # Check if company name is taken
        if Company.objects.filter(name=company_name).exists():
            return render(request, "pennywise/register.html", {
                "message": "Company name already taken."
            })
        
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "pennywise/register.html", {
                "message": "Username already taken."
            })
        
        # Create company
        company = Company(name=company_name, user=user)
        company.save()

        # Create company-user relation
        company_user = CompanyUser(user=user, company=company, access_level = 1)
        company_user.save()

        login(request, user)
        companies = []
        for company in user.owned_companies.all():
            companies.append(company.name)
        request.session['company'] = user.owned_companies.all()[0].name
        request.session['companies'] = companies
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "pennywise/register.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            list_of_owned_companies = []
            owned_companies = user.owned_companies.all()
            for company in owned_companies:
                list_of_owned_companies.append(company.name)
            request.session["company"] = owned_companies[0].name
            request.session["company_id"] = owned_companies[0].id
            request.session["companies"] = list_of_owned_companies
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "pennywise/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "pennywise/login.html")
    

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required
def index(request):
    message = None
    error = None
    came_from_income = False # By default the page loads on the expenses tab, this variable changes to the income tab if a form was sent from income
    if request.method == "POST":
        settle_description = request.POST["settle_description"]
        amount = request.POST["amount"]
        settle_date = request.POST["settle_date"]
        transaction_id = request.POST["transaction_id"]
        transaction = Transaction.objects.get(id=transaction_id)
        try:
            account = Account.objects.get(id=request.POST["account_id"])
        except:
            account = None
            error = "Must select an account."
            if transaction.category.type == "I":
                came_from_income = True

        if account:
            # Update transaction with settle information
            transaction.settle_description = settle_description
            transaction.amount = amount
            transaction.settle_date = settle_date
            transaction.settle_user = request.user
            transaction.settle_account = account
            transaction.save()

            date = datetime.strptime(settle_date, "%Y-%m-%d").replace(day=1).date()
            # Try to get an instance of the account's monthly balance, creates one if it doesn't exist
            try:
                monthly_balance = MonthlyAccountBalance.objects.get(account=account, month_year=date)
            except:
                monthly_balance = MonthlyAccountBalance(account=account, month_year=date)

            # Update account balance
            if transaction.category.type == "E":
                account.balance = float(account.balance) - float(amount)
                monthly_balance.balance = float(monthly_balance.balance) - float(amount)
            else:
                account.balance = float(account.balance) + float(amount)
                monthly_balance.balance = float(monthly_balance.balance) + float(amount)
                came_from_income = True

            account.save()
            monthly_balance.save()
            message = "Transaction settled successfully."

    accounts = Account.objects.filter(company=request.session["company_id"])
    today = datetime.today().date()
    upcoming = today + timedelta(15)
    todays_expenses = Transaction.objects.filter(category__type="E", due_date__lte=today, company=request.session["company_id"], settle_date__isnull=True).order_by("due_date")
    upcoming_expenses = Transaction.objects.filter(category__type="E", due_date__range=(today+timedelta(1), upcoming), company=request.session["company_id"], settle_date__isnull=True).order_by("due_date")
    settled_expenses = Transaction.objects.filter(category__type="E", company=request.session["company_id"], settle_date=today).order_by("due_date")
    todays_incomes = Transaction.objects.filter(category__type="I", due_date__lte=today, company=request.session["company_id"], settle_date__isnull=True).order_by("due_date")
    upcoming_incomes = Transaction.objects.filter(category__type="I", due_date__range=(today+timedelta(1), upcoming), company=request.session["company_id"], settle_date__isnull=True).order_by("due_date")
    settled_incomes = Transaction.objects.filter(category__type="I", company=request.session["company_id"], settle_date=today).order_by("due_date")
    
    return render(request, "pennywise/index.html", {
        "accounts": accounts,
        "todays_expenses": todays_expenses,
        "upcoming_expenses": upcoming_expenses,
        "settled_expenses": settled_expenses,
        "todays_incomes": todays_incomes,
        "upcoming_incomes": upcoming_incomes,
        "settled_incomes": settled_incomes,
        "came_from_income": came_from_income,
        "message": message,
        "error": error
    })

@login_required
def new_transaction(request):
    expense_categories = Category.objects.filter(type="E").order_by("name")
    income_categories = Category.objects.filter(type="I").order_by("name")
    message = None

    if request.method == "POST":
        due_date = datetime.strptime(request.POST["due_date"], "%Y-%m-%d").date()
        try:
            category = Category.objects.get(id=request.POST["category"])
        except:
            return render(request, "pennywise/new_transaction.html", {"expense_categories": expense_categories, "income_categories": income_categories, "error":"Must choose category."})

        amount = float(request.POST["amount"])
        payment_info = request.POST["payment_info"]
        description = request.POST["description"]
        replicate = request.POST["replicate"]
        has_installments = request.POST.get("has_installments", False)
        installments = request.POST["installments"]
        company = Company.objects.get(id=request.session["company_id"])

        if has_installments:
            new_date = due_date
            for n in range(int(installments)):
                transaction = Transaction(company=company, user=request.user, due_date=new_date, category=category, amount=amount, payment_info=payment_info, description=description, replicate=replicate, installments=installments, current_installment=int(n)+1)
                transaction.save()
                new_date = due_date + relativedelta(months = int(n)+1)
        else:
            transaction = Transaction(company=company, user=request.user, due_date=due_date, category=category, amount=amount, payment_info=payment_info, description=description, replicate=replicate)
            transaction.save()
        message = "Transaction saved successfully."

    return render(request, "pennywise/new_transaction.html", {
        "expense_categories": expense_categories,
        "income_categories": income_categories,
        "message": message
    })


@login_required
def archive(request):
    if request.method == "POST":
        try:
            from_date = datetime.strptime(request.POST["from_date"], "%Y-%m-%d").date()
        except ValueError:
            from_date = None
        try:
            to_date = datetime.strptime(request.POST["to_date"], "%Y-%m-%d").date()
        except ValueError:
            to_date = None
        search = request.POST["search"]
        is_unsettled = bool(request.POST["is_unsettled"])
        expense_income_option = request.POST["expense_income_option"]

        if(from_date and to_date):
            search_data = Transaction.objects.filter(company= request.session["company_id"], due_date__gte=from_date, due_date__lte=to_date, description__icontains=search, category__type=expense_income_option, settle_date__isnull=is_unsettled).order_by("due_date")
        elif(from_date):
            search_data = Transaction.objects.filter(company= request.session["company_id"], due_date__gte=from_date, description__icontains=search, category__type=expense_income_option, settle_date__isnull=is_unsettled).order_by("due_date")
        elif(to_date):
            search_data = Transaction.objects.filter(company= request.session["company_id"], due_date__lte=to_date, description__icontains=search, category__type=expense_income_option, settle_date__isnull=is_unsettled).order_by("due_date")
        else:
            search_data = Transaction.objects.filter(company= request.session["company_id"], description__icontains=search, category__type=expense_income_option, settle_date__isnull=is_unsettled).order_by("due_date")

        data_paginator = Paginator(search_data, 10)
        try:
            page_num = request.POST['page']
        except:
            page_num = None
        page = data_paginator.get_page(page_num)
        iterator = range(1,page.paginator.num_pages+1)
        max_page = max(iterator)

        search_parameters = {
            "from": from_date,
            "to": to_date,
            "search": search,
            "is_unsettled": is_unsettled,
            "expense_income_option": expense_income_option
        }

        return render(request, "pennywise/archive.html", {
            "search_parameters": search_parameters,
            "page": page,
            "iterator": iterator,
            "max_page": max_page
        })


    return render(request, "pennywise/archive.html")


@login_required
def edit(request):
    
    if request.method == "POST":
        transaction = Transaction.objects.get(id=request.POST["transaction_id"])
        old_amount = float(transaction.amount)

        try:
            account = Account.objects.get(id=request.POST["account"])
        except:
            account = None

        if request.POST["edit"] == "edit_transaction":
            due_date = datetime.strptime(request.POST["due_date"], "%Y-%m-%d").date()
            try:
                settle_date = datetime.strptime(request.POST["settle_date"], "%Y-%m-%d").date()
                old_settle_month_year = transaction.settle_date.replace(day=1)
            except ValueError:
                settle_date = None

            category = Category.objects.get(id=request.POST["category"])
            amount = float(request.POST["amount"])
            payment_info = request.POST["payment_info"]
            description = request.POST["description"]
            settle_description = request.POST["settle_description"]
            transaction.due_date = due_date
            transaction.settle_date = settle_date
            transaction.category = category
            transaction.amount = amount
            transaction.payment_info = payment_info
            transaction.description = description
            transaction.settle_description = settle_description

            # Check if transaction has been settled and adjust account balance
            if (transaction.settle_date):
                old_account = Account.objects.get(id = transaction.settle_account.id)
                if (transaction.settle_account != account):
                    if (transaction.category.type == "E"):
                        old_account.balance = float(old_account.balance) + old_amount
                        account.balance = float(account.balance) - transaction.amount
                    else:
                        old_account.balance = float(old_account.balance) - old_amount
                        account.balance = float(account.balance) + transaction.amount
                    old_account.save()
                    account.save()
                    transaction.settle_account = account

                elif (old_amount != amount):
                    if (transaction.category.type == "E"):
                        account.balance = float(account.balance) + old_amount
                        account.balance = float(account.balance) - amount
                    else:
                        account.balance = float(account.balance) - old_amount
                        account.balance = float(account.balance) + amount
                    account.save()
                '''
                Ver isso aqui
                Mudando a conta, tem que mudar o monthlyaccountbalance de qualquer jeito, se não mudar a conta, tem que ver se mudou o mêsano
                VER SE DEU CERTO ISSO AÊ
                '''
                old_account_monthly_balance = MonthlyAccountBalance.objects.get(account=old_account, month_year=old_settle_month_year)
                try:
                    account_monthly_balance = MonthlyAccountBalance.objects.get(account=account, month_year=settle_date.replace(day=1))
                except:
                    account_monthly_balance = MonthlyAccountBalance(account=account, month_year=settle_date.replace(day=1))

                # This conditional checks if the account or month is different
                if (old_account_monthly_balance != account_monthly_balance):
                    if (transaction.category.type == "E"):
                        old_account_monthly_balance.balance = float(old_account_monthly_balance.balance) + old_amount
                        account_monthly_balance.balance = float(account_monthly_balance.balance) - amount
                    else:
                        old_account_monthly_balance.balance = float(old_account_monthly_balance.balance) - old_amount
                        account_monthly_balance.balance = float(account_monthly_balance.balance) + amount
                    
                    old_account_monthly_balance.save()
                    account_monthly_balance.save()

                elif (old_amount != amount):
                    if (transaction.category.type == "E"):
                        account_monthly_balance.balance = float(account_monthly_balance.balance) + old_amount
                        account_monthly_balance.balance = float(account_monthly_balance.balance) - amount
                    else:
                        account_monthly_balance.balance = float(account_monthly_balance.balance) - old_amount
                        account_monthly_balance.balance = float(account_monthly_balance.balance) + amount
                    account_monthly_balance.save()

                transaction.save()
                message = "Transaction edited successfully."
       
        elif request.POST["edit"] == "delete_transaction":
            if (transaction.settle_date):
                account_monthly_balance = MonthlyAccountBalance.objects.get(account=account, month_year=transaction.settle_date.replace(day=1))
                if (transaction.category.type == "E"):
                    account.balance = float(account.balance) + old_amount
                    account_monthly_balance.balance = float(account_monthly_balance.balance) + old_amount
                else:
                    account.balance = float(account.balance) - old_amount
                    account_monthly_balance.balance = float(account_monthly_balance.balance) - old_amount
                account.save()
                account_monthly_balance.save()

            transaction.delete()
            message = "Transaction deleted successfully."

        return render(request, "pennywise/archive.html", {
            "message": message
        })
    
    transaction = Transaction.objects.get(id=request.GET.get("transaction_id"))
    accounts = Account.objects.filter(company=request.session["company_id"])
    if (transaction.category.type == "E"):
        categories = Category.objects.filter(type="E").order_by("name")
    else:
        categories = Category.objects.filter(type="I").order_by("name")
        
    return render(request, "pennywise/edit.html", {
        "transaction": transaction,
        "accounts": accounts,
        "categories": categories
    })


@login_required
def accounts(request):
    today = datetime.today().date()
    error = None
    
    if request.method == "POST":
        account = Account.objects.get(id=request.POST["account"])
        date = datetime.strptime(request.POST["date"], "%Y-%m").date().replace(day=1)
        transactions = Transaction.objects.filter(settle_account=account, settle_date__month=date.month, settle_date__year=date.year)
        if not transactions:
            error = "No activity for the selected month"
        else:
            month_difference = relativedelta(today, date)
            month_difference = month_difference.years * 12 + month_difference.months
            month_balance = float(MonthlyAccountBalance.objects.get(account=account, month_year=date).balance)
            carry_over = 0
            for i in range(month_difference):
                try:
                    carry_over = carry_over + float(MonthlyAccountBalance.objects.get(account=account, month_year=date+relativedelta(months=i+1)).balance)
                except:
                    pass
            carry_over = float(account.balance) - (carry_over + month_balance)
            balance = carry_over + month_balance

        
            return render(request, "pennywise/account_statement.html", {
                "account": account,
                "transactions": transactions,
                "carry_over": carry_over,
                "month_balance": month_balance,
                "balance": balance,
                "date": date.strftime("%B %Y")
            })

    accounts = Account.objects.filter(company=request.session["company_id"])
    return render(request, "pennywise/accounts.html", {
        "accounts": accounts,
        "today": today,
        "error": error
    })

@login_required
def overview(request):
    return render(request, "pennywise/overview.html")

@login_required
def settings(request):
    message = None
    error = None
    if request.method == "POST":
        company = Company.objects.get(name=request.session["company"])
        # Save new category
        if request.POST["option"] == "new_category":
            new_category = request.POST["new_category"].title()
            type = request.POST["category_type"]
            category = Category(name=new_category, type=type, company=company)
            try:
                category.save()
                message = "New category saved."
            except IntegrityError:
                error = "Category name unavailable."

        
        # Save new account
        elif request.POST["option"] == "new_account":
            new_account = request.POST["new_account"].title()
            starting_balance = float(request.POST["starting_balance"])
            account = Account(name=new_account, balance=starting_balance, company=company)
            account_monthly_balance = MonthlyAccountBalance(account=account, balance=starting_balance, month_year=datetime.today().date().replace(day=1))
            try:
                account.save()
                account_monthly_balance.save()
                message = "New account saved."
            except IntegrityError:
                error = "Account name unavailable."

    return render(request, "pennywise/settings.html", {
        "message": message,
        "error": error,
    })