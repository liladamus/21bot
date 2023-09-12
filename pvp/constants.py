# Set the actual contract address and bot private key here
# Replace with your contract address

BOT_PRIVATE_KEY = ''
BOT_ADDRESS = ''
CHAIN_ID = 5
GAS_LIMIT = 2000000
BLOCK_SCANNER = "goerli.etherscan.io"
WEBSOCKET_PROVIDER_URL = ''
GAS_ADJUSTMENT = 1.4

GAME_CA = ''
PVP_CA = ''

GAME_ABI = [
    {
        "inputs": [
            {
                "internalType": "int64",
                "name": "_tgChatId",
                "type": "int64"
            },
            {
                "internalType": "uint256",
                "name": "_minBet",
                "type": "uint256"
            },
            {
                "internalType": "address[]",
                "name": "_players",
                "type": "address[]"
            },
            {
                "internalType": "uint256[]",
                "name": "_bets",
                "type": "uint256[]"
            },
            {
                "internalType": "bool",
                "name": "_useWETH",
                "type": "bool"
            }
        ],
        "name": "newGame",
        "outputs": [
            {
                "internalType": "uint256[]",
                "name": "",
                "type": "uint256[]"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "int64",
                "name": "_tgChatId",
                "type": "int64"
            },
            {
                "internalType": "address",
                "name": "_winner",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "_loser",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "_winnerChipsWei",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_loserChipsWei",
                "type": "uint256"
            },
            {
                "internalType": "bool",
                "name": "_usedWETH",
                "type": "bool"
            }
        ],
        "name": "endGame",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bool",
                "name": "usedWETH",
                "type": "bool"
            }
        ],
        "name": "abortAllGames",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

PVP_ABI = [{
    "inputs": [{"internalType": "uint32", "name": "secret", "type": "uint32"}],
    "name": "connectAndApprove",
    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
    "stateMutability": "nonpayable",
    "type": "function",
},
    {
        "inputs": [{"internalType": "uint32", "name": "secret", "type": "uint32"}],
        "name": "getStoredAddress",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "sender", "type": "address"},
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]
