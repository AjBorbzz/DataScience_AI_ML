sample_email_data = [
    # 1. Phishing Email - Fake Bank Alert
    {
        "email_subject": "Urgent: Your Account Has Been Locked!",
        "from_name": "Chase Bank",
        "from_address": "support@chase-verification.com",
        "to_address": "user@example.com",
        "headers": "Received-SPF: fail (domain mismatch); DKIM: none; DMARC: fail",
        "email_body": "Dear customer, your Chase account was locked due to suspicious activity. Verify now: http://chase-verification-login.com",
        "attachment_names_and_hashes": "",
        "list_of_urls": ["http://chase-verification-login.com"],
        "qr_data": ""
    },

    # 2. Phishing Email - Fake Invoice with Malware
    {
        "email_subject": "Invoice Due - Action Required",
        "from_name": "Accounts Payable",
        "from_address": "invoice@paypal-secure.com",
        "to_address": "employee@business.com",
        "headers": "SPF: softfail; DKIM: fail; DMARC: fail",
        "email_body": "See attached invoice. Overdue balance must be settled within 24 hours to avoid penalties.",
        "attachment_names_and_hashes": "invoice_1245.pdf (SHA256: e3b0c44298fc1c14...ffb6c1)",
        "list_of_urls": [],
        "qr_data": ""
    },

    # 3. Phishing Email - QR Code Phish
    {
        "email_subject": "Confirm Your Delivery - DHL",
        "from_name": "DHL Express",
        "from_address": "tracking@dhl-delivery.link",
        "to_address": "customer@domain.com",
        "headers": "SPF: fail; DKIM: none; DMARC: fail",
        "email_body": "We missed your delivery. Scan QR code to reschedule.",
        "attachment_names_and_hashes": "",
        "list_of_urls": [],
        "qr_data": "http://dhl-schedule-confirm.com/track"
    },

    # 4. Legitimate Email - GitHub Notification
    {
        "email_subject": "[GitHub] New sign-in to your account",
        "from_name": "GitHub",
        "from_address": "noreply@github.com",
        "to_address": "dev@example.com",
        "headers": "SPF: pass; DKIM: pass; DMARC: pass",
        "email_body": "New sign-in from Firefox on macOS. If this was you, no action is needed.",
        "attachment_names_and_hashes": "",
        "list_of_urls": ["https://github.com/settings/sessions"],
        "qr_data": ""
    },

    # 5. Legitimate Email - Receipt from Online Purchase
    {
        "email_subject": "Your Apple Receipt",
        "from_name": "Apple",
        "from_address": "no-reply@apple.com",
        "to_address": "user@icloud.com",
        "headers": "SPF: pass; DKIM: pass; DMARC: pass",
        "email_body": "Thanks for your purchase. Your receipt is attached and also available online.",
        "attachment_names_and_hashes": "receipt_4578.pdf (SHA256: 5f4dcc3b5aa765d61d8327deb882cf99...)",
        "list_of_urls": ["https://apple.com/bill"],
        "qr_data": ""
    }
]