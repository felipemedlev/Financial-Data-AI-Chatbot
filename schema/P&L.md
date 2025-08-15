# CompanyName Mapping Rules - P&L Data Schema

## CRITICAL MAPPING RULES

### Base Company Name Transformations (ALWAYS APPLY FIRST)
**These mappings are MANDATORY and case-insensitive:**

| User Input | Maps To |
|------------|---------|
| `Falabella Retail` | `Total Retail` |
| `Retail` | `Total Retail` |
| `Sodimac` | `Total Sodimac` |
| `Tottus` | `Total Tottus` |

### Country-Specific Mapping Logic

#### When Country is Specified
If user mentions a specific country, append it to the mapped company name:

**Examples:**
- `"Falabella Retail Chile"` → Search for: `"Total Retail Chile"`
- `"Retail Chile"` → Search for: `"Total Retail Chile"`
- `"Sodimac Peru"` → Search for: `"Total Sodimac Peru"`
- `"Tottus Colombia"` → Search for: `"Total Sodimac Colombia"`

#### When NO Country is Specified (Aggregated Data)
If user asks for company without country, sum ALL countries where that company operates:

**Falabella Retail / Retail (no country specified):**
- Search and SUM: `"Total Retail Chile"` + `"Total Retail Argentina"` + `"Total Retail Peru"` + `"Total Retail Colombia"`

**Sodimac (no country specified):**
- Search and SUM: `"Total Sodimac Chile"` + `"Total Sodimac Argentina"` + `"Total Sodimac Peru"` + `"Total Sodimac Colombia"` + `"Total Sodimac Brasil"` + `"Total Sodimac Uruguay"` + `"Total Sodimac Mexico"`

**Tottus (no country specified):**
- Search and SUM: `"Total Tottus Chile"` + `"Total Tottus Peru"`

## STEP-BY-STEP MAPPING PROCESS

### Step 1: Identify Base Company
- Look for: "Falabella Retail", "Retail", "Sodimac", or "Tottus" in user query
- Apply base transformation (see table above)

### Step 2: Check for Country Specification
- If country mentioned → Use mapped name + country
- If NO country mentioned → Aggregate across ALL countries

### Step 3: Execute Query
- Search CompanyName column for exact mapped values
- For aggregation: SUM values across all matching country variations

## COMMON USER QUERIES & CORRECT MAPPINGS

| User Query | Correct CompanyName Search | Action |
|------------|---------------------------|---------|
| "Retail Chile performance" | `"Total Retail Chile"` | Single country search |
| "Falabella Retail Argentina" | `"Total Retail Argentina"` | Single country search |
| "Show me Retail data" | `"Total Retail Chile"`, `"Total Retail Argentina"`, `"Total Retail Peru"`, `"Total Retail Colombia"` | Sum all countries |
| "Sodimac results" | `"Total Sodimac Chile"`, `"Total Sodimac Argentina"`, `"Total Sodimac Peru"`, `"Total Sodimac Colombia"`, `"Total Sodimac Brasil"`, `"Total Sodimac Uruguay"`, `"Total Sodimac Mexico"` | Sum all countries |
| "Tottus Peru" | `"Total Tottus Peru"` | Single country search |
| "How is Tottus doing?" | `"Total Tottus Chile"`, `"Total Tottus Peru"` | Sum all countries |

## ERROR PREVENTION CHECKLIST

Before executing any query, verify:

**Base company name transformed correctly**
- "Falabella Retail" or "Retail" → "Total Retail"
- "Sodimac" → "Total Sodimac"
- "Tottus" → "Total Tottus"

**Country logic applied correctly**
- Country specified → Single country search
- No country specified → Multi-country aggregation

**CompanyName values match exactly**
- Use exact strings: "Total Retail Chile", "Total Sodimac Argentina", etc.
- Case doesn't matter in search, but use consistent casing

## AVAILABLE COUNTRIES BY COMPANY

**Total Retail operates in:**
- Chile, Argentina, Peru, Colombia

**Total Sodimac operates in:**
- Chile, Argentina, Peru, Colombia, Brasil

**Total Tottus operates in:**
- Chile, Peru

## IMPORTANT NOTES

1. **NEVER use original company names** ("Falabella Retail", "Sodimac", "Tottus") in CompanyName searches
2. **ALWAYS use mapped names** ("Total Retail", "Total Sodimac", "Total Tottus")
3. **Country aggregation is the DEFAULT** when no specific country is mentioned
4. **All mappings are case-insensitive** for user input recognition
5. **CompanyName searches must be exact** for the mapped values