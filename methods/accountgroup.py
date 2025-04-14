# Define valid account groups as a set for quick membership testing.
VALID_ACCOUNT_GROUPS = {
    "0001",  # Sold-to party
    "0002",  # Goods recipient
    "0003",  # Payer
    "0004",  # Bill-to party
    "0005",  # Prospective customer
    "0006",  # Competitor
    "0007",  # Sales partners
    "0012",  # Hierarchy Node
    "0100",  # Distribution center
    "0110",  # Branch w/o intercomp.billing
    "0120",  # Branch with intercomp.billing
    "0130",  # Branch with external billing
    "0140",  # Assortment (obsolete,don't use)
    "0150",  # Franchisee
    "0160",  # Wholesale customer
    "0170",  # Consumer
    "CPD",   # One-time cust.(int.no.assgnmt)
    "CPDA",  # One-time cust.(ext.no.assgnmt)
    "DEBI",  # Customer (general)
    "KUNA",  # Customer (ext.number assgnmnt)
    "LCMS",  # Customer(Portal Role), Minimal
    "LCMX",  # Customer (Portal Role), Maxim.
    "VVD",   # TR-LO customer
    "X001",  # Trade Organization
    "X002",  # End Customer
    "YB01",  # Sold-to party (ext. number)
    "YB02",  # Sold-to party (ext.char.code)
    "YB03",  # Sold-to party (int. no.) Demo
    "YBAC",  # Customer (affiliated company)
    "YBEC",  # Export Customers
    "YBOC",  # CPD Customer (external no.)
    "YBPC",  # Dummy customer
    "YBVC",  # Vendor
    "Z001",  # CRM Customer
    "Z002",  # ECC-Sold to party
    "Z003",  # Bill to party
    "Z004",  # Ship to party
    "Z005",  # Payer
    "Z006",  # Commission Agent
    "Z007",  # Vendor Returns
    "Z008",  # Group Customer
    "Z009",  # One time customers
    "Z010",  # STO
    "Z011",  # Inter Company
    "Z012",  # Prospective customer
    "Z013",  # Others
    "Z014",  # Treasury Customers
    "Z015",  # Reference Institutionals
    "Z016",  # Challan JW/TRC
    "Z017",  # Employee Customer
    "Z018",  # Ship from
    "Z023",  # End Customer
    "ZNRM",  # NorAm Customers
    "ZX01",  # Vx: GPO/Buying Group
    "ZX02",  # Vx: End Customers
}

def validate_account_group(account_group):
    return account_group in VALID_ACCOUNT_GROUPS