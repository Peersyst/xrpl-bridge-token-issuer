import json
import xrpl

# Load config ------------------------------------------------------------------
with open("config.json", "r") as f:
    config = json.load(f)

node_url = config.get("node_url")
faucet_host = config.get("faucet_host")
issuer_seed = config.get("issuer_seed")
currency_code = config.get("currency_code")
seed = config.get("seed")
issue_quantity = config.get("issue_quantity")

# Connect ----------------------------------------------------------------------
client = xrpl.clients.JsonRpcClient(node_url)

# Configure issuer (cold address) settings -------------------------------------
if issuer_seed:
    cold_wallet = xrpl.wallet.generate_faucet_wallet(client, xrpl.wallet.Wallet(seed=issuer_seed, sequence=0), False, faucet_host)
    cold_wallet_info = xrpl.account.get_account_info(cold_wallet.classic_address, client)
    cold_wallet.sequence = cold_wallet_info.result.get("account_data").get("Sequence")
else:
    cold_wallet = xrpl.wallet.generate_faucet_wallet(client, None, False, faucet_host)

cold_settings_tx = xrpl.models.transactions.AccountSet(
    account=cold_wallet.classic_address,
    transfer_rate=0,
    tick_size=5,
    domain=bytes.hex("example.com".encode("ASCII")),
    set_flag=xrpl.models.transactions.AccountSetFlag.ASF_DEFAULT_RIPPLE,
)
cst_prepared = xrpl.transaction.safe_sign_and_autofill_transaction(
    transaction=cold_settings_tx,
    wallet=cold_wallet,
    client=client,
)
print("➡️ Sending issuer address AccountSet transaction...")
response = xrpl.transaction.send_reliable_submission(cst_prepared, client)
print("✔️ Cold address AccountSet transaction success!\n")

# Create trust line from hot to cold address -----------------------------------
hot_wallet = xrpl.wallet.Wallet(seed=seed, sequence=0)
hot_wallet_info = xrpl.account.get_account_info(hot_wallet.classic_address, client)
hot_wallet.sequence = hot_wallet_info.result.get("account_data").get("Sequence")

trust_set_tx = xrpl.models.transactions.TrustSet(
    account=hot_wallet.classic_address,
    limit_amount=xrpl.models.amounts.issued_currency_amount.IssuedCurrencyAmount(
        currency=currency_code,
        issuer=cold_wallet.classic_address,
        value="10000000000", # Large limit, arbitrarily chosen
    )
)
ts_prepared = xrpl.transaction.safe_sign_and_autofill_transaction(
    transaction=trust_set_tx,
    wallet=hot_wallet,
    client=client,
)
print("➡️ Creating trust line from receiver address to issuer...")
response = xrpl.transaction.send_reliable_submission(ts_prepared, client)
print("✔️ Trust line created successfully!\n")

# Send token -------------------------------------------------------------------
send_token_tx = xrpl.models.transactions.Payment(
    account=cold_wallet.classic_address,
    destination=hot_wallet.classic_address,
    amount=xrpl.models.amounts.issued_currency_amount.IssuedCurrencyAmount(
        currency=currency_code,
        issuer=cold_wallet.classic_address,
        value=issue_quantity
    )
)
pay_prepared = xrpl.transaction.safe_sign_and_autofill_transaction(
    transaction=send_token_tx,
    wallet=cold_wallet,
    client=client,
)
print(f"➡️ Sending {issue_quantity} {currency_code} to {hot_wallet.classic_address}...")
response = xrpl.transaction.send_reliable_submission(pay_prepared, client)
print(f"✔️ {issue_quantity} {currency_code} were sent successfully to {hot_wallet.classic_address}!\n\n")

# Summary ---------------------------------------------------------------
print("➡️ Getting summary...")
response = client.request(xrpl.models.requests.AccountLines(
    account=hot_wallet.classic_address,
    ledger_index="validated",
))
print("✔️ Summary:")
print(f"    - Issuer address: {cold_wallet.classic_address}")
print(f"    - Token code: {currency_code}")
print(f"    - Token quantity: {issue_quantity}")
print(f"    - Receiver address: {hot_wallet.classic_address}")

print("\n")
print("✅ Done!")