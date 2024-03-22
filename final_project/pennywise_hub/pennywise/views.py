from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from .models import User, Company, CompanyUser, Category, Account, Transaction

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

            # Update account balance
            if transaction.category.type == "E":
                account.balance = float(account.balance) - float(amount)
            else:
                account.balance = float(account.balance) + float(amount)
                came_from_income = True

            account.save()
            message = "Transaction settled successfully."

    accounts = Account.objects.filter(company=request.session["company_id"])
    today = datetime.today().date()
    upcoming = today + timedelta(15)
    todays_expenses = Transaction.objects.filter(category__type="E", due_date__lte=today, company=request.session["company_id"], settle_date__isnull=True).order_by("due_date")
    upcoming_expenses = Transaction.objects.filter(category__type="E", due_date__range=(today+timedelta(1), upcoming), company=request.session["company_id"], settle_date__isnull=True).order_by("due_date")
    settled_expenses = Transaction.objects.filter(category__type="E", due_date=today, company=request.session["company_id"], settle_date__isnull=False).order_by("due_date")
    todays_incomes = Transaction.objects.filter(category__type="I", due_date__lte=today, company=request.session["company_id"], settle_date__isnull=True).order_by("due_date")
    upcoming_incomes = Transaction.objects.filter(category__type="I", due_date__range=(today+timedelta(1), upcoming), company=request.session["company_id"], settle_date__isnull=True).order_by("due_date")
    settled_incomes = Transaction.objects.filter(category__type="I", due_date=today, company=request.session["company_id"], settle_date__isnull=False).order_by("due_date")
    
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
                print(f'{int(n)+1} de {installments}')
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
            try:
                account.save()
                message = "New account saved."
            except IntegrityError:
                error = "Account name unavailable."

    return render(request, "pennywise/settings.html", {
        "message": message,
        "error": error,
    })