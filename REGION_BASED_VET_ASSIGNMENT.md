# Region-Based Vet Assignment System

## ✅ Feature Implemented: Regional Vet Matching

The system now **triggers and shows only vets from the same region** (province) as the farmer when a disease is predicted as SEVERE or CRITICAL.

---

## 🎯 How It Works

### **1. Farmer Submits Symptoms**
- Farmer selects symptoms and submits case
- ML model predicts disease and confidence
- System classifies severity: NON_SEVERE, SEVERE, or CRITICAL

### **2. Severity-Based Actions**

#### **NON-SEVERE (Confidence ≥ 70%)**
- ✅ Shows home treatment recommendations
- ✅ No vet needed
- ✅ Farmer follows self-care instructions

#### **SEVERE (50% ≤ Confidence < 70%)**
- ⚠️ **System triggers ALL vets in farmer's province**
- ⚠️ Farmer directed to vet selection page
- ⚠️ Shows ONLY vets who serve farmer's province
- ⚠️ Farmer chooses preferred vet
- ⚠️ Selected vet is assigned to case

#### **CRITICAL (Confidence < 50%)**
- 🚨 **System auto-assigns nearest vet from farmer's province**
- 🚨 Emergency protocols triggered
- 🚨 No manual selection needed (automatic assignment)
- 🚨 Assigned vet notified immediately

---

## 🗺️ Regional Matching Logic

### **How Vets are Filtered by Region:**

```python
# Step 1: Get farmer's location
Farmer Location:
  - Province: "Harare"
  - District: "Harare Urban"

# Step 2: Find all approved vets
- Query all vets with is_approved=True and is_available=True

# Step 3: Filter by province
- Check each vet's provinces_served field (JSON array)
- Example: ["Harare", "Mashonaland East", "Bulawayo"]
- If farmer's province ("Harare") is in vet's provinces_served
  → Include vet in results
- If not → Exclude vet

# Step 4: Calculate distance (if GPS available)
- If both farmer and vet have GPS coordinates
  → Calculate distance using Haversine formula
  → Sort by distance (nearest first)
- If GPS not available
  → Sort alphabetically by name

# Step 5: Show to farmer
- Display all matching vets from same region
- Farmer selects preferred vet
- System assigns selected vet to case
```

---

## 🔧 Technical Implementation

### **1. New Functions in `vets/utils.py`**

#### `find_vets_by_region(province, district)`
```python
def find_vets_by_region(province: str, district: str = None) -> List[Tuple[Vet, float]]:
    """
    Find all approved and available vets in the same region (province/district) as the farmer.
    
    Returns:
        List of tuples (Vet, distance) where distance is None if GPS not available
    """
```

**What it does:**
- Gets all approved vets
- Filters vets who serve the farmer's province
- Checks `provinces_served` JSON field for matches
- Case-insensitive matching ("Harare" matches "harare")
- Returns list of vets sorted by name

#### `find_vets_by_region_with_distance(province, district, farmer_lat, farmer_lon)`
```python
def find_vets_by_region_with_distance(...) -> List[Tuple[Vet, float]]:
    """
    Find all approved vets in the same region, WITH distance calculation if GPS available.
    
    Returns:
        List of tuples (Vet, distance_km) sorted by distance (nearest first)
    """
```

**What it does:**
- Calls `find_vets_by_region()` to get vets in same province
- Calculates distance for each vet (if both have GPS)
- Uses Haversine formula for accurate distance
- Sorts by distance (nearest first)
- Vets without GPS go to end of list

### **2. Updated `farmers/views.py`**

#### `submit_case()` view - Line 103
**Changes:**
- **CRITICAL cases**: Now uses `find_vets_by_region_with_distance()` instead of `find_nearby_vets()`
- **SEVERE cases**: Updated message to mention region

**Before:**
```python
# Old code - GPS-based only
nearby_vets = find_nearby_vets(farmer.latitude, farmer.longitude, radius=50)
```

**After:**
```python
# New code - Region-based first, then GPS
vets_in_region = find_vets_by_region_with_distance(
    province=farmer.province,
    district=farmer.district,
    farmer_lat=farmer.latitude,
    farmer_lon=farmer.longitude
)
```

#### `select_vet()` view - Line 187
**Changes:**
- Now finds vets by region instead of GPS radius
- Shows farmer's province in context
- Validates selected vet serves farmer's province
- Better error messages mentioning region

**Key Validation:**
```python
# Double-check vet serves this province
if isinstance(vet.provinces_served, list):
    provinces_lower = [p.lower().strip() for p in vet.provinces_served]
    if farmer.province.lower().strip() not in provinces_lower:
        messages.error(request, 'Selected vet does not serve your region.')
        return redirect('farmers:select_vet', case_id=case.id)
```

### **3. Enhanced UI `templates/farmers/select_vet.html`**

**New Features:**
- 🗺️ Shows farmer's location (Province + District)
- 📊 Displays total count of vets in region
- 📍 Shows distance to each vet (if GPS available)
- 🎨 Improved card design with hover effects
- 📱 Fully responsive layout
- ✨ Interactive selection (entire card clickable)
- 🔍 Clear visual feedback for selected vet

---

## 📊 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  FARMER SUBMITS CASE                                        │
│  Symptoms: ['cough', 'fever', 'nasal_discharge']           │
│  Location: Province="Harare", District="Harare Urban"      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ML PREDICTION                                              │
│  Disease: "Bovine Respiratory Disease"                     │
│  Confidence: 0.62 (62%)                                    │
│  Severity: SEVERE (50% ≤ 0.62 < 70%)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  TRIGGER VETS IN SAME REGION                               │
│  find_vets_by_region_with_distance(                        │
│      province="Harare",                                     │
│      district="Harare Urban",                              │
│      farmer_lat=-17.8292,                                  │
│      farmer_lon=31.0522                                    │
│  )                                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  FILTER VETS                                                │
│                                                             │
│  All Vets in Database: 20 vets                            │
│      ↓                                                      │
│  Filter: is_approved=True, is_available=True: 18 vets     │
│      ↓                                                      │
│  Filter: Serves "Harare" province                          │
│      ├─ Dr. John Moyo (Harare, Mashonaland East) ✓       │
│      ├─ Dr. Sarah Ncube (Harare, Harare Urban) ✓         │
│      ├─ Dr. Peter Chiweshe (Bulawayo, Matabeleland) ✗    │
│      ├─ Dr. Mary Sibanda (Harare, Chitungwiza) ✓         │
│      └─ Dr. James Khumalo (Mutare, Manicaland) ✗         │
│      ↓                                                      │
│  Result: 3 vets in Harare                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  CALCULATE DISTANCES (if GPS available)                    │
│                                                             │
│  Farmer GPS: -17.8292, 31.0522                            │
│                                                             │
│  Dr. John Moyo    (GPS: -17.8350, 31.0480) → 1.2 km      │
│  Dr. Sarah Ncube  (GPS: -17.8100, 31.0600) → 3.5 km      │
│  Dr. Mary Sibanda (GPS: None) → Distance N/A              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  SORT BY DISTANCE                                           │
│                                                             │
│  1. Dr. John Moyo - 1.2 km away                           │
│  2. Dr. Sarah Ncube - 3.5 km away                         │
│  3. Dr. Mary Sibanda - Distance N/A                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  SHOW VET SELECTION PAGE                                   │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │ Your Location: Harare, Harare Urban              │     │
│  │ Found 3 qualified vets in Harare                 │     │
│  │                                                   │     │
│  │ ☐ Dr. John Moyo - 1.2 km away                   │     │
│  │   License: VET12345                              │     │
│  │   Experience: 10 years                           │     │
│  │   Phone: +263771234567                           │     │
│  │                                                   │     │
│  │ ☐ Dr. Sarah Ncube - 3.5 km away                 │     │
│  │   License: VET67890                              │     │
│  │   Experience: 7 years                            │     │
│  │   Phone: +263779876543                           │     │
│  │                                                   │     │
│  │ ☐ Dr. Mary Sibanda - Distance N/A                │     │
│  │   License: VET11111                              │     │
│  │   Experience: 15 years                           │     │
│  │   Phone: +263775555555                           │     │
│  │                                                   │     │
│  │        [Confirm Selection]                        │     │
│  └──────────────────────────────────────────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  FARMER SELECTS VET                                        │
│  Selected: Dr. John Moyo                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  VALIDATE SELECTION                                         │
│  ✓ Vet is approved                                         │
│  ✓ Vet serves farmer's province (Harare)                  │
│  ✓ Vet is available                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  ASSIGN VET TO CASE                                        │
│  Case #15:                                                 │
│    - Farmer: John Farmer (Harare)                         │
│    - Disease: Bovine Respiratory Disease                  │
│    - Assigned Vet: Dr. John Moyo                          │
│    - Status: ASSIGNED                                      │
│                                                             │
│  Message: "✅ Dr. John Moyo has been assigned to your     │
│            case. They will contact you soon."             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  VET NOTIFIED (Future Enhancement)                         │
│  - Email notification to Dr. John Moyo                     │
│  - SMS alert                                                │
│  - Dashboard notification                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌍 Province-Based Matching Examples

### **Example 1: Farmer in Harare**

**Farmer:**
- Name: John Farmer
- Province: Harare
- District: Harare Urban

**Available Vets:**
1. Dr. John Moyo - Serves: [Harare, Mashonaland East] ✅ **MATCHES**
2. Dr. Sarah Ncube - Serves: [Harare] ✅ **MATCHES**
3. Dr. Peter Chiweshe - Serves: [Bulawayo, Matabeleland South] ❌ NO MATCH
4. Dr. Mary Sibanda - Serves: [Harare, Chitungwiza] ✅ **MATCHES**
5. Dr. James Khumalo - Serves: [Mutare, Manicaland] ❌ NO MATCH

**Result:** Farmer sees 3 vets (Dr. Moyo, Dr. Ncube, Dr. Sibanda)

---

### **Example 2: Farmer in Bulawayo**

**Farmer:**
- Name: Mary Dube
- Province: Bulawayo
- District: Bulawayo Central

**Available Vets:**
1. Dr. Peter Chiweshe - Serves: [Bulawayo, Matabeleland South] ✅ **MATCHES**
2. Dr. John Moyo - Serves: [Harare, Mashonaland East] ❌ NO MATCH
3. Dr. Thabo Ndlovu - Serves: [Bulawayo, Matabeleland North] ✅ **MATCHES**

**Result:** Farmer sees 2 vets (Dr. Chiweshe, Dr. Ndlovu)

---

### **Example 3: No Vets in Region**

**Farmer:**
- Name: Grace Musariri
- Province: Matabeleland North
- District: Binga

**Available Vets:**
1. Dr. John Moyo - Serves: [Harare, Mashonaland East] ❌ NO MATCH
2. Dr. Sarah Ncube - Serves: [Harare] ❌ NO MATCH
3. Dr. Peter Chiweshe - Serves: [Bulawayo] ❌ NO MATCH

**Result:** No vets found. System shows:
- ⚠️ "No Vets Available in Your Region"
- 📞 Emergency contact information
- 🏛️ Ministry of Agriculture contact
- 💡 Suggestion to check neighboring provinces

---

## 🎨 UI Features

### **Vet Selection Page Components:**

1. **Location Header**
   - Shows farmer's province and district
   - Gradient background (orange theme)
   - Clear visual hierarchy

2. **Vet Count Banner**
   - "Found X qualified vets in [Province]"
   - Success alert (green)
   - Motivates farmer that help is available

3. **Vet Cards**
   - Radio button selection
   - Hover effects (lifts up)
   - Distance badge (if GPS available)
   - Full vet details:
     - License number
     - Qualification
     - Experience (years)
     - Phone number (clickable)
     - Provinces served (badges)

4. **Interactive Features**
   - Entire card is clickable
   - Visual feedback when selected
   - Smooth animations
   - Mobile-responsive

5. **Distance Display**
   - Green badge if distance calculated: "1.2 km away"
   - Gray badge if no GPS: "Distance N/A"
   - Sorted by distance (nearest first)

---

## 📱 Mobile Responsiveness

### **Desktop (> 768px)**
- 2 vet cards per row
- Wider cards with more space
- Side-by-side comparison easy

### **Tablet (577px - 768px)**
- 2 cards per row (narrower)
- Responsive padding

### **Mobile (< 576px)**
- 1 card per row (full width)
- Touch-friendly radio buttons
- Larger tap targets
- Scrollable list

---

## ✅ Benefits of Region-Based System

### **1. Relevant Matches**
- ✅ Farmers only see vets who actually serve their area
- ✅ No confusion with vets from distant provinces
- ✅ Higher likelihood vet can physically visit farm

### **2. Regulatory Compliance**
- ✅ Respects provincial boundaries
- ✅ Vets work in regions they're registered for
- ✅ Easier for Ministry to monitor

### **3. Practical Logistics**
- ✅ Reduced travel time for vets
- ✅ Vets familiar with local diseases
- ✅ Vets know local farming practices

### **4. Better User Experience**
- ✅ Clear location-based filtering
- ✅ Farmer knows vet is nearby
- ✅ Builds trust in system

### **5. Scalability**
- ✅ Works even without GPS
- ✅ Can add more provinces easily
- ✅ Simple to understand logic

---

## 🔍 How to Test

### **Test 1: SEVERE Case - Vet Selection**

1. Login as farmer from Harare
2. Submit case with symptoms that give 50-70% confidence
3. System classifies as SEVERE
4. Click to select vet
5. **Expected**: See only vets who serve Harare
6. Select a vet
7. **Expected**: Success message, vet assigned

### **Test 2: CRITICAL Case - Auto Assignment**

1. Login as farmer from Bulawayo
2. Submit case with symptoms that give < 50% confidence
3. System classifies as CRITICAL
4. **Expected**: Nearest vet from Bulawayo auto-assigned
5. **Expected**: Emergency message displayed

### **Test 3: No Vets Available**

1. Login as farmer from province with no vets
2. Submit SEVERE case
3. **Expected**: Warning message about no vets
4. **Expected**: Emergency contact information

### **Test 4: GPS Distance Calculation**

1. Login as farmer with GPS coordinates
2. Submit SEVERE case
3. View vet selection page
4. **Expected**: Vets sorted by distance
5. **Expected**: Distance badges showing km

---

## 🚀 Summary

**What Was Implemented:**
- ✅ Region-based vet filtering (by province)
- ✅ Triggers ALL vets in same province
- ✅ Shows distance if GPS available
- ✅ Farmer selects preferred vet
- ✅ Beautiful vet selection UI
- ✅ Validation of vet-region match
- ✅ Emergency handling for no vets
- ✅ Mobile-responsive design

**Result:**
- 🎯 Farmers only see vets from their region
- 🎯 NO vets from different provinces shown
- 🎯 System respects provincial boundaries
- 🎯 Clear, professional UI
- 🎯 Works with or without GPS

**The system now correctly triggers and shows ONLY vets from the same region as the farmer!** 🎉
