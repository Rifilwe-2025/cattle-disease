# Vet Registration Links - Quick Guide

## 📋 Your Approved Vets

You have **3 approved vet applications** waiting for registration:

---

### **1. Dr. Ruvimbo Chikowore**
- **Email:** rchikowore@vetmail.co.zw
- **Phone:** 0784567123
- **License:** VET-ZW-2017-0239
- **Status:** PENDING REGISTRATION

**Registration Link:**
```
http://127.0.0.1:8000/vets/register/2/
```

---

### **2. Dr. Knowledge Maphosa**
- **Email:** kmaphosa@gmail.com
- **Phone:** 0771982345
- **License:** ZVPC-2020-0894
- **Status:** PENDING REGISTRATION

**Registration Link:**
```
http://127.0.0.1:8000/vets/register/3/
```

---

### **3. Dr. Tawanda Ncube**
- **Email:** tawanda.ncube@vetmail.co.zw
- **Phone:** 0780311387
- **License:** VET-ZW-2019-0456
- **Status:** PENDING REGISTRATION

**Registration Link:**
```
http://127.0.0.1:8000/vets/register/1/
```

---

## 📧 How to Send Registration Links

### **Option 1: Email Template**

Copy this template and send to each vet:

```
Subject: Complete Your Vet Registration - Cattle Disease Prediction System

Dear Dr. [Name],

Congratulations! Your application to join the Cattle Disease Prediction System has been APPROVED!

Please complete your registration by clicking the link below:
[REGISTRATION LINK]

You will need to:
1. Create a username and password
2. Verify your contact information
3. Set your practice location
4. Set your availability status

Once registered, you can:
- Login to the vet dashboard
- Receive case assignments from farmers
- Provide veterinary consultations
- Help farmers in your region

If you have any questions, please contact us.

Regards,
Ministry of Agriculture
Cattle Disease Prediction System
```

---

### **Option 2: SMS Template**

```
Dear Dr. [Name], your vet application has been approved!
Complete registration: [SHORT LINK]
Contact: [YOUR PHONE]
```

---

### **Option 3: Direct Contact**

1. Call each vet
2. Inform them of approval
3. Read out or send the registration link
4. Guide them through registration if needed

---

## 🔄 How It Works

```
1. You send registration link to vet
   ↓
2. Vet clicks link
   ↓
3. Vet sees registration form (pre-filled with application data)
   ↓
4. Vet fills:
   - Username
   - Password
   - Email (verify)
   - Phone (verify)
   - Province & District
   - GPS location (optional)
   - Availability status
   ↓
5. Vet submits form
   ↓
6. System creates account
   ↓
7. Vet can now login and access dashboard
```

---

## ✅ To Check Future Registration Links

Run this command anytime:

```bash
python get_vet_registration_links.py
```

This will show:
- All approved applications
- Their registration status
- Links for those not yet registered
- Email templates ready to copy

---

## 🔍 To Check if a Vet Has Registered

The script will show:
- **[PENDING REGISTRATION]** - Link still needs to be used
- **[ALREADY REGISTERED]** - Vet has completed registration

---

## 📱 Registration Link Format

```
http://127.0.0.1:8000/vets/register/<application_id>/

Examples:
http://127.0.0.1:8000/vets/register/1/
http://127.0.0.1:8000/vets/register/2/
http://127.0.0.1:8000/vets/register/3/
```

**Important:** Each link is unique to each vet's application!

---

## 🚨 Important Notes

1. **Links Only Work Once** - After a vet registers, the link won't work again (shows "already registered" message)

2. **Application Must Be Approved** - Link only works if application status = APPROVED

3. **No Login Required** - Vets don't need to login to access registration form

4. **Secure** - Each link is tied to a specific approved application

---

## 📞 What to Tell Vets

When contacting approved vets, inform them:

1. ✅ Their application has been approved
2. 📧 They'll receive a registration link
3. 🔐 They need to create username & password
4. 📍 They can add GPS location to help farmers find them
5. ⏱️ Registration takes ~5 minutes
6. 🎯 Once registered, they can start receiving cases

---

## 🎉 After Registration

Once vets register, they can:
- ✅ Login with their username/password
- ✅ Access vet dashboard
- ✅ View assigned cases
- ✅ Provide consultations
- ✅ Manage their availability
- ✅ Update their profile

---

## 💡 Tips

1. **Send Links Promptly** - Vets are waiting for approval notification
2. **Follow Up** - Check if they completed registration after a few days
3. **Provide Support** - Some vets may need help with registration
4. **Keep Records** - Note when you sent each link
5. **Verify Registration** - Run the script again to confirm they registered

---

## 📊 Current Status

**Total Approved Applications:** 3
**Pending Registration:** 3
**Already Registered:** 0

**Action Required:**
- Send registration links to all 3 vets
- Monitor registration completion
- Follow up if needed

---

## 🆘 Troubleshooting

### **Vet says link doesn't work:**
1. Check if application is approved
2. Verify application ID in link
3. Check if vet already registered
4. Try regenerating link

### **Vet can't complete registration:**
1. Check form validation errors
2. Verify username is unique
3. Ensure password meets requirements
4. Check internet connection

### **Need to resend link:**
1. Run `python get_vet_registration_links.py`
2. Copy the link again
3. Send via different method (email/SMS/call)

---

## 📧 Example Email (Ready to Send)

**To: rchikowore@vetmail.co.zw**

```
Subject: Complete Your Vet Registration

Dear Dr. Ruvimbo Chikowore,

Congratulations! Your application to join the Cattle Disease Prediction System has been APPROVED!

Please complete your registration by clicking the link below:
http://127.0.0.1:8000/vets/register/2/

You'll need to create a username and password to access the system.

Once registered, you can login and start receiving case assignments from farmers in your region.

If you have any questions, please don't hesitate to contact us.

Best regards,
Ministry of Agriculture
```

---

## ✅ Next Steps

1. **Copy each registration link above**
2. **Send to corresponding vet via email/SMS**
3. **Monitor registration completion** (run script again in 2-3 days)
4. **Follow up** with vets who haven't registered
5. **Welcome them** once they complete registration

**All 3 vets are ready to be contacted!** 🎉
