# Info

HBF offers its members two main types of health insurance products - hospital and extras. Hospital products cover in-hospital costs when admitted for treatment, while extras is for out of hospital health expenses like dental, physio, optical etc. Hospital products may have an excess (typically $0/$250/$500 per adult on the policy) while extras benefits are set dollar amounts for each type of treatment, with the customer paying the rest of the charge. 

Private health insurance is further complicated by a risk pooling system between all funds known as Risk Equalisation (RE). This applies for hospital products only. Based on the age of a member, a percentage of benefits paid nominally goes into a pool (this is 0% under the age of 55% and ramps up to 88% at about age 80). The average cost per member across all funds is then calculated and funds that have paid less than the average pay an amount to funds that have paid more than the average, to ensure that all funds are equal. This means funds with young, low claiming members tend to pay into the pool where funds with older, higher claiming members (like HBF) tend to receive money from the pool. This also varies between a funds products, depending on what demographic they attract with products targetted at younger members paying into the pool, and products for older members receiving from the pool. There is more information on this here: https://www.actuaries.asn.au/Library/Events/SUM/2017/SUM17ReidEtAlPaper.pdf

This workbook contains the following data:
- DATA_policies: The number of policies and income/premiums paid broken down by the members' combination of hospital and extras product held, quarterly for CY 2025-2026.
- DATA_hosp_claims: Quarterly hospital claims by product and claim category
- DATA_ext_claims: Quarterly extras claims by product and claim category
- DATA_RE: This is the net receipt (+ amount) or payment (- amount) into the risk equalisation pool by hospital product and quarter.
- DATA_product_movements: Total sales, cancellations and movements on and off our hospital and extras products by quarter. 

There are further definitions on each sheet. 

HBF typically considers the margins on a product to be Total Premiums - Total Claims + Risk Equalisation

# Field descriptions

## DATA_policies

Quarter: The quarter (by calendar year)
Hosp: The name of the hospital product held - Basic/Mid/Top or No Hospital Product
Hosp Excess: The excess per adult applicable for that group of policies
Extras:	The name of the extras product held - Entry/Standard/Premium or No Extras Product
hospital_income: Total premiums paid for hospital products by members with the given combination of hospital/extras
extras_income: Total premiums paid for extras products by members with the given combination of hospital/extras
policies: The number of policies that held the given combination of hospital/extras at the end of the quarter

## DATA_hosp_claims

Quarter: The quarter (by calendar year)
Hosp: The name of the hospital product held - Bronze/Silver/Gold or No Hospital Product
Hosp Excess: The excess per adult applicable for that group of policies
CLAIM_CATEGORY: What the claim was for 
TOTAL_FEES_CHARGED: Total fees charged for all in hospital treatments on that product/excess/claim category
TOTAL_BENEFIT: Total benefits paid by HBF for hospital treatments on that product/excess/claim category
BED_DAYS: Total days spent in hospital on that product/excess/claim category
Episodes: Number of stays in/admissions to hospital on that product/excess/claim category

## DATA_ext_claims

Quarter: The quarter (by calendar year)
Extras: The name of the extras product held - Entry/Standard/Premium or No Extras Product
CLAIM_CATEGORY: What the claim was for 
TOTAL_FEES_CHARGED: Total fees charged for all ancillary treatments on that product/claim category
TOTAL_BENEFIT: Total benefits paid by HBF for ancillary treatments on that product/claim category
TOTAL_SERVICES: Total ancillary services claimed by members on that product/claim category eg. One visit to a physio or one pair of glasses

## DATA_RE

Quarter: The quarter (by calendar year)
Hosp: The name of the hospital product held - Bronze/Silver/Gold or No Hospital Product
Hosp Excess: The excess per adult applicable for that group of policies
RE Received: The net payment from the risk equalisation pool corresponding to members on the given product/excess. Note a positive amount means the product received a payment (for older, higher claiming members) and this offsets claim costs. A negative amount means the product paid into the pool (for younger, lower claiming members) and this increases the fund's cost of offering that product.

## DATA_product_movements_hosp

Quarter: The quarter (by calendar year)
Hosp: The name of the hospital product held - Bronze/Silver/Gold or No Hospital Product
Hosp Excess: The excess per adult applicable for that group of policies
Type: Hospital Sale - a policy who didn't previously hold hospital took out a hospital product. Hospital Cancellation - a policy drops their hospital cover. Hospital Move On - An existing policy changes their cover and takes out this product. Hospital Move Off - An existing policy changes their cover and drops this product. Note: net movements on and off in a quarter should always balance.
Movements: Total number of policies taking this action with respect to the given product/excess

## DATA_product_movements_ext

Quarter: The quarter (by calendar year)
Extras: The name of the extras product held - Entry/Standard/Premium or No Extras Product
Type: Ext Sale - a policy who didn't previously hold hospital took out a hospital product. Ext Cancellation - a policy drops their hospital cover. Ext Move On - An existing policy changes their cover and takes out this product. Ext Move Off - An existing policy changes their cover and drops this product. Note: net movements on and off in a quarter should always balance.
Movements: Total number of policies taking this action with respect to the given product