import pandas as pd
import json
import re
from tqdm import tqdm
tqdm.pandas()
from phonenumbers import is_valid_number, parse, NumberParseException
from methods.cityClustering import *
from methods.postalcodes import *
from methods.accountgroup import *
from methods.gstpan import *
from methods.industrytype import *
from methods.customerSegment import *
from methods.companyCode import *
from methods.glCode import *
from methods.dunningProcedure import *
from methods.accAssignment import *
from methods.salesOrg import *
from methods.distChannel import *
from methods.division import *
from methods.priceProcedure import *
from methods.incoterms import *
from methods.shippingConditions import *
from methods.billingStateCode import *
from methods.industryCode1 import *
from methods.businessUnit import *
from methods.portfolio import *
from methods.salesOrderBlocking import *
from methods.accountGroupVendor import *
from methods.companyCodeVendor import *
from methods.planningGroup import *
from methods.toleranceGroup import *
from methods.purchaseOrganization import *
from methods.purchasingGroup import *
from methods.incotermsVendor import *
from methods.msmeStatus import *
from methods.abacStatusVendor import *
from methods.confControlsVendor import *
from methods.glCodeVendor import *
from methods.blockFunctionVendor import *
from methods.paymentTermsVendor import *
from methods.materialType import *
from methods.plant import *
from methods.accountAssignmentMaterial import *
from methods.materialGroup import *
from methods.QMControl import *
from methods.loadingGroup import *
from methods.profitCenter import *
from methods.mrpType import *
from methods.industryMaterial import *
from methods.purchaseGroupMaterial import *
from methods.valuationCategory import *
from methods.availabilityCheck import *
from methods.valuationClass import *
from methods.unitOfMeasurement import *
from methods.mrpController import *
from methods.transGroupMat import *
from methods.purchValueKeyMat import *

# def standardizeDate(value):
#     try:        
#         dt = pd.to_datetime(value, dayfirst=False)
#         ist = pytz.timezone('Asia/Kolkata')        
#         if dt.tzinfo is None:
#             dt = ist.localize(dt)
#         else:
#             dt = dt.astimezone(ist)        
#         standardized_date = dt.strftime("%Y-%m-%d %H:%M:%S")
#         return str(standardized_date) == str(value)
#     except Exception:
#         return False

def validate_phone_number(number, region):
    try:
        parsed_number = parse(number, region)
        return is_valid_number(parsed_number)
    except NumberParseException:
        return False
    
def load_rules(path):
    with open(path, 'r') as rules:
        rules_json = json.load(rules)      
    return rules_json.get("rules", [])

def check_rule(df, row, value, rule, refcol):
    rtype = rule.get("rule")
    # print(value)
    if rtype == 'not_null':
        # print(f'[NOT NULL]\n{value}')
        return pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan'
            
    elif rtype == 'capitalization':
        if (pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan'):
            return False
        else:
            return not value == value.title()
    
    elif rtype == 'phone-regex':
        try:
            cond1 = bool(re.match(rule.get("expression"),value))
            cond2 = validate_phone_number(str(value),refcol)
            return not (cond1 and cond2)
        except:
            return False
    
    elif rtype == 'regex':
        # print(bool(re.match(rule.get("expression"),value.strip())))
        # print(value.strip())
        try:
            str(int(float(value)))
        except:
            return not bool(re.match(rule.get("expression"),value.strip()))
        return not bool(re.match(rule.get("expression"),str(int(float(value)))))
    
    elif rtype == 'unique':
        # print(list(df[rule.get("column")]).count(value) > 1)
        # print(list(df[rule.get("column")]).count(value))
        if not (pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan'):
            return list(df[rule.get("column")].astype(str)).count(value) > 1
    
    elif rtype == 'validation-postal-code':
        if (pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan'):
            return False
        else:
            try:
                return not validate_postal_code(value, refcol)
            except:
                return False
    
    elif rtype == 'combined-not-null':
        isNull = True
        for col in rule.get("combined"):
            val = str(row[col])
            isNull = isNull and (pd.isnull(val) or str(val).strip() == '' or val.lower() == 'nan')
        return isNull
    
    elif rtype == 'validation-acc-group':
        return not validate_account_group(value)
    
    elif rtype == 'validation-industry-type':
        return not validate_industry_type(value)
    
    elif rtype == 'gst-pan-valid':
        try:
            if refcol.upper() == 'IN':
                if rule.get('column') == 'Tax Number 3' or rule.get('column') == 'GST_Number__c': 
                    return not validate_gst_pan_number(value,isGST=True)
                else: 
                    return not validate_gst_pan_number(value,isPan=True)
        except:
            return False
        
    elif rtype == 'gst-pan-not-null':
        # print(value)
        # print(type(value))
        try:
            if refcol.upper() == 'IN':
                return pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan'
        except:
            return False
    
    elif rtype == 'validation-date':
        try:
            pd.to_datetime(value)
        except:
            return True
        return False
    
    elif rtype == 'numeric':
        try: 
            n = float(value)
            return not n.is_integer()
        except:
            return True
        return False
    
    elif rtype == 'alpha-numeric':
        return not str(value).isalnum()
    
    elif rtype == 'validation-customer-segment':
        return not validate_customer_segment(value)
    
    elif rtype == 'validation-company-code':
        return not validate_company_code(value)
    
    elif rtype == 'validation-gl-code':
        return not validate_gl_codes(refcol, value)
    
    elif rtype == 'validation-dunning':
        return not validate_dunning(value)
    
    elif rtype == 'validation-acc-assignment':
        return not validate_acc_assignment(value)
    
    elif rtype == 'validation-sales-org':
        return not validate_sales_org(value)
    
    elif rtype == 'validation-dist-channel':
        return not validate_dist_channel(value)
    
    elif rtype == 'validation-division':
        return not validate_division(value)
    
    elif rtype == 'validation-price-procedure':
        return not validate_price_procedure(value)
    
    elif rtype == 'validation-incoterms':
        return not validate_incoterms(value)
    
    elif rtype == 'validation-shipping-conditions':
        return not validate_shipping_conditions(value)
    
    elif rtype == 'validation-billing-state-code':
        return not validate_billingStateCode(refcol, value)
    
    elif rtype == 'validation-industry-code-type':
        return not validate_industry_code(value)
    
    elif rtype == 'validation-BU':
        return not validateBU(value)
    
    elif rtype == 'validation-portfolio':
        return not validatePortfolio(value)
    
    elif rtype == 'validation-customer-category':
        return not value.lower() in ['existing', 'hunting'] 
    
    elif rtype == 'validation-sales-order-blocking':
        return not validate_sales_order_blocking(value)
    
    elif rtype == 'validation-account-group-vendor':
        return not validate_account_group_vendor(value)
    
    elif rtype == 'validation-company-code-vendor':
        return not validate_company_code_vendor(value)
    
    elif rtype == 'validation-planning-group':
        return not validate_planning_group(value)
    
    elif rtype == 'validation-tolerance-group':
        return not validate_tolerance_group(value)
    
    elif rtype == 'validation-purchase-organization':
        return not validate_purchase_org(value)
    
    elif rtype == 'validation-purchase-group':
        return not validate_purchasing_group(value)
    
    elif rtype == 'validation-x':
        return not (value == 'X' or pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan')
    
    elif rtype == 'validation-incoterms-vendor':
        return not validate_incoterms_vendor(value)
    
    elif rtype == 'validation-msme-status':
        return not validate_msme_number(value)
    
    elif rtype == 'standard-msme-number':
        if str(refcol) == '0.0' or str(refcol) == '0' or str(refcol) == '00':
            pass
        else:
            if not (pd.isnull(refcol) or str(refcol).strip() == '' or str(refcol).lower() == 'nan'):
                return not bool(re.match(rule.get("expression"),value.strip())) 
    
    elif rtype == 'msme_not_null':
        if str(refcol) == '0.0' or str(refcol) == '0' or str(refcol) == '00':
            pass
        else:
            if not (pd.isnull(refcol) or str(refcol).strip() == '' or str(refcol).lower() == 'nan'):
                return pd.isnull(value) or str(value).strip() == '' or value.lower() == 'nan'
        
    elif rtype == 'validation-abac':
        return not validate_abac_status(value)
    
    elif rtype == 'validation-confirmation-control':
        return not validate_confirmation_controls(value)
    
    elif rtype == 'validation-glCode-vendor':
        return not validate_gl_codes_vendor(value)
    
    elif rtype == 'supplier-regex':
        if refcol == 'Z001':
            try:
                str(int(float(value)))
            except:
                return not bool(re.match(rule.get("domestic_exp"),value.strip()))
            return not bool(re.match(rule.get("domestic_exp"),str(int(float(value)))))
        elif refcol == 'Z002':
            try:
                str(int(float(value)))
            except:
                return not bool(re.match(rule.get("import_exp"),value.strip()))
            return not bool(re.match(rule.get("import_exp"),str(int(float(value)))))
        elif refcol == 'Z014':
            try:
                str(int(float(value)))
            except:
                return not bool(re.match(rule.get("bonded_exp"),value.strip()))
            return not bool(re.match(rule.get("bonded_exp"),str(int(float(value)))))
        
    elif rtype == 'advance-country':
        if refcol == 'Z001':
            return not str(value).upper() == 'IN'
        if refcol == 'Z002':
            return str(value).upper() == 'IN'
        
    elif rtype == 'validation-block-function':
        if not (pd.isnull(refcol) or str(refcol).strip() == '' or str(refcol).lower() == 'nan'):
            return not validateBlockFunction(value)
    
    elif rtype == 'validation-payment-terms':
        return not validatePaymentTermsVendor(value)
    
    elif rtype == 'validation-material':
        return not validateMaterialType(value)
    
    elif rtype == 'validation-plant':
        return not validatePlant(value)
    
    elif rtype == 'validation-length':
        return not bool(re.fullmatch(rule.get('expression'),value))
    
    elif rtype == 'validation-account-assignment':
        return not validateAccountAssignment(value)
    
    elif rtype == 'validation-mat-group':
        return not validateMaterialGroup(value)
    
    elif rtype == 'validation-qmcontrol':
        return not validateQMControl(value)
    
    elif rtype == 'validation-loading-group':
        return not validateLoadingGroup(value)
    
    elif rtype == 'validation-profit-center':
        return not validateProfitCenter(value)
    
    elif rtype == 'validation-mrp-type':
        return not validateMRP_type(value)
    
    elif rtype == 'validation-mat-industry':
        return not validateIndustryMaterial(value)
    
    elif rtype == 'validation-purch-group-mat':
        return not validatePurchaseGroupMaterial(value)

    elif rtype == 'validation-valuation-cat':
        return not validateValuationCat(value)
    
    elif rtype == 'validation-avail-check':
        return not validateAvailCheck(value)
    
    elif rtype == 'validation-valuation-class':
        return not validateValuationClass(value)
    
    elif rtype == 'validation-uom':
        return not validateUOM(value)
    
    elif rtype == 'validation-mrp-controller':
        return not validateMRPcontroller(int(float(refcol)), value)
    
    elif rtype == 'validation-incoterms-2-vendor':
        inco = str(row['Incoterms'])
        if int(float(refcol)) == 5100:
            if inco.upper() == 'DAP' or inco.upper() == 'CIF':
                return str(value).title() != 'Bangalore' or str(value).title() != 'Bengaluru'
        elif int(float(refcol)) == 5500:
            if inco.upper() == 'DAP' or inco.upper() == 'CIF':
                return str(value).title() != 'Hyderabad'
        if inco.upper() == 'EXW':
                return str(value).title() != str(row['City']).title()
            
    elif rtype == 'validation-trans-group-mat':
        return not validateTransGroupMat(value)
    
    elif rtype == 'validation-purch-val-key-mat':
        return not validatePurchValMat(value)

    else:
        raise Exception(f"Rule type {rtype} does not exist")
    
        
def check_row(df, row,rules):
    issues = []
    prev_rule = ''
    prev_col = ''
    num_issues = 0
    categories = []
    # print(row)
    for rule in rules:           
        refcol = ''
        col = rule.get("column")        
        message = rule.get("message", f"Issue with {col}")
        rule_category = rule.get("rule_category")
        if prev_col != '' and rule.get('rule') != prev_rule and col == prev_col:
            continue
        if 'ref' in rule.keys():
            refcol = row[rule.get('ref')]
            # print(refcol)
        if col in row:
            if check_rule(df, row, str(row[col]).strip(), rule, refcol):
                issues.append(message)
                categories.append(rule_category)
                num_issues += 1
                prev_rule = rule.get('rule')
                prev_col = col
        else:
            # print("Column absent")
            issues.append(f"Column {col} not found")
    return {"Issues": ", ".join(issues),"Count of issues":num_issues, "Issue categories": ", ".join(set(categories))}

def apply_rules(df, rules):
    # print(pd.DataFrame(df.apply(lambda row: check_row(row, rules), axis=1), index=))
    df["Issues"] = df.progress_apply(lambda row: check_row(df, row, rules), axis=1)
    df_new = df['Issues'].progress_apply(pd.Series)
    df = df.drop('Issues',axis=1).join(df_new)
    return df