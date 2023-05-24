# XRPL Bridge Token Issuer

Scripts to issue xrpl tokens in the xrpl bridge devnet.

## Setup

Install the xrpl package:

```sh
pip install xrpl-py
```

Set config:

```json
{
    "node_url": "http://sidechain-net1.devnet.rippletest.net:51234",
    "currency_code": "TST",
    "seed": "sEd7nEkquz3AKirhJBKvwYWswewygVh",
    "issue_quantity": 1000000,
    "faucet_host": "sidechain-faucet.devnet.rippletest.net",
    "issuerSeed": //Optional
}
```

## Usage

```sh
python issuer.py
```
