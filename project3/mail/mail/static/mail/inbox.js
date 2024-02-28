document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email(0));

  // Event listener when composed e-mail is submitted 
  document.querySelector('#compose-form').addEventListener('submit', event => {
    send_email();
    event.preventDefault();
  })

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email(id) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  if (id === 0) {
    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  }
  else {
    fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {
      document.querySelector('#compose-recipients').value = `${email.sender}`;
      if (email.subject.slice(0,3) === 'Re:') {
        document.querySelector('#compose-subject').value = `${email.subject}`;
      }
      else {
        document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
      }
      document.querySelector('#compose-body').value = `\n...\nOn ${email.timestamp} ${email.sender} wrote: \n${email.body}`;
    })
  }
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Show mailbox's emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    if (emails.length > 0) {
      const table = document.createElement('table');
      table.classList.add('table')
      table.classList.add('table-bordered')
      table.classList.add('table-hover')
      emails.forEach((email) => {
        let shown_email;
        let tr;
        if (mailbox === 'sent') {
          shown_email = email.recipients
        }
        else {
          shown_email = email.sender
        }
        if (email.read === true && mailbox === 'inbox') {
          tr = `<tr onclick="load_email(${email.id})" style="background-color: lightgray;"><td><b>`
        }
        else {
          tr = `<tr onclick="load_email(${email.id})"><td><b>`
        }
        let row = tr + shown_email + '</b></td>' + '<td style="text-align: left;">' + email.subject + '</td>' + '<td style= color:gray;>' + email.timestamp + '</td></tr>';
        table.innerHTML += row;
      })
      document.querySelector('#emails-view').appendChild(table);
    }
  })
}

function send_email() {
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
    load_mailbox('sent');
  })
}

function load_email(id) {
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
      let content = `<p><b>From:</b> ${email.sender} <br> <b>To:</b> ${email.recipients} <br> <b>Subject:</b> ${email.subject} <br> <b>Timestamp:</b> ${email.timestamp}</p> <hr> ${email.body.replaceAll("\n", "<br>")} <hr>`;
      document.querySelector('#emails-view').innerHTML = content;
      // Check if email is not sent by current user, create a button if not
      if (email.sender != document.querySelector('h2').innerHTML) {
        // Set reply button and function
        const reply_button = document.createElement('button');
        reply_button.innerHTML = 'Reply';
        reply_button.classList.add('btn-primary');
        reply_button.addEventListener('click', () => compose_email(id));
        // Set archive button and function
        const archive_button = document.createElement('button');
        archive_button.classList.add('btn-primary');
        archive_button.style.margin = '0px 0px 0px 10px'
        if (email.archived === false) {
          archive_button.innerHTML = 'Archive';
        }
        else {
          archive_button.innerHTML = 'Unarchive';
        }
        archive_button.addEventListener('click', () => {
          fetch(`/emails/${id}`, {
            method: 'PUT',
            body: JSON.stringify({
                archived: !email.archived
            })
          })
          // Timeout to fix a bug that made the archived email still appear in the inbox, even tho it was already archived
          .then(setTimeout(() => {
            load_mailbox('inbox')
          }, 50))
        })
        document.querySelector('#emails-view').appendChild(reply_button);        
        document.querySelector('#emails-view').appendChild(archive_button);
      }
  });
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
}