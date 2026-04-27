from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

QTC_DARK   = HexColor('#0a0e1a')
QTC_BLUE   = HexColor('#1a3a6b')
QTC_ACCENT = HexColor('#2563eb')
QTC_LIGHT  = HexColor('#e8f0fe')
QTC_GRAY   = HexColor('#6b7280')
QTC_SILVER = HexColor('#f1f5f9')
WHITE      = HexColor('#ffffff')

doc = SimpleDocTemplate(
    "QTOP_Whitepaper.pdf",
    pagesize=letter,
    rightMargin=0.85*inch, leftMargin=0.85*inch,
    topMargin=0.85*inch,   bottomMargin=0.85*inch,
    title="Qubit TopCoin (QTOP) Whitepaper",
    author="Porter Kowalski"
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle('T', fontSize=28, fontName='Helvetica-Bold',
    textColor=WHITE, alignment=TA_CENTER, spaceAfter=6, leading=34)
subtitle_style = ParagraphStyle('S', fontSize=13, fontName='Helvetica',
    textColor=HexColor('#93c5fd'), alignment=TA_CENTER, spaceAfter=4, leading=18)
ticker_style = ParagraphStyle('Tk', fontSize=16, fontName='Helvetica-Bold',
    textColor=HexColor('#60a5fa'), alignment=TA_CENTER, spaceAfter=20)
h1_style = ParagraphStyle('H1', fontSize=16, fontName='Helvetica-Bold',
    textColor=QTC_ACCENT, spaceBefore=18, spaceAfter=8, leading=20)
h2_style = ParagraphStyle('H2', fontSize=12, fontName='Helvetica-Bold',
    textColor=QTC_BLUE, spaceBefore=12, spaceAfter=6, leading=16)
body_style = ParagraphStyle('B', fontSize=10, fontName='Helvetica',
    textColor=HexColor('#1e293b'), alignment=TA_JUSTIFY, spaceAfter=8, leading=15)
quote_style = ParagraphStyle('Q', fontSize=11, fontName='Helvetica-BoldOblique',
    textColor=QTC_BLUE, alignment=TA_CENTER, spaceBefore=12, spaceAfter=12,
    leading=16, leftIndent=30, rightIndent=30)
caption_style = ParagraphStyle('C', fontSize=8, fontName='Helvetica',
    textColor=QTC_GRAY, alignment=TA_CENTER, spaceAfter=4)

def make_table(data, col_widths, header_bg=None):
    t = Table(data, colWidths=col_widths)
    style = [
        ('BACKGROUND', (0,0), (-1,0), header_bg or QTC_DARK),
        ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, QTC_SILVER]),
        ('FONTSIZE',   (0,0), (-1,-1), 9),
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('GRID',       (0,0), (-1,-1), 0.5, HexColor('#cbd5e1')),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]
    t.setStyle(TableStyle(style))
    return t

elements = []

# COVER
header_data = [[Paragraph("QUBIT TOPCOIN", title_style)]]
header_table = Table(header_data, colWidths=[6.8*inch])
header_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), QTC_DARK),
    ('TOPPADDING', (0,0), (-1,-1), 40),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ('LEFTPADDING', (0,0), (-1,-1), 20),
    ('RIGHTPADDING', (0,0), (-1,-1), 20),
]))
elements.append(header_table)

sub_data = [
    [Paragraph("A Quantum-Resistant, CPU-Mined Cryptocurrency", subtitle_style)],
    [Paragraph("for Everyone, Forever", subtitle_style)],
    [Paragraph("QTOP", ticker_style)],
]
sub_table = Table(sub_data, colWidths=[6.8*inch])
sub_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), QTC_BLUE),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 20),
    ('RIGHTPADDING', (0,0), (-1,-1), 20),
]))
elements.append(sub_table)
elements.append(Spacer(1, 0.3*inch))

stats = [
    ["MAX SUPPLY", "BLOCK TIME", "SIGNATURES", "MINING"],
    ["21,000,000 QTOP", "2.5 Minutes", "FALCON-512", "RandomX CPU"],
]
stats_table = Table(stats, colWidths=[1.7*inch]*4)
stats_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), QTC_ACCENT),
    ('BACKGROUND', (0,1), (-1,1), QTC_LIGHT),
    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
    ('TEXTCOLOR',  (0,1), (-1,1), QTC_DARK),
    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTNAME',   (0,1), (-1,1), 'Helvetica-Bold'),
    ('FONTSIZE',   (0,0), (-1,0), 8),
    ('FONTSIZE',   (0,1), (-1,1), 10),
    ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING',    (0,0), (-1,-1), 10),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ('GRID',       (0,0), (-1,-1), 0.5, WHITE),
]))
elements.append(stats_table)
elements.append(Spacer(1, 0.3*inch))

principles = [
    ["No Premine", "NIST Standardized", "FALCON-512 P2P", "CPU Mining"],
    ["100% fair launch\nEvery QTOP earned\nthrough mining",
     "FALCON-512 approved\nby NIST in 2024",
     "Node identity uses\npost-quantum\nauthentication",
     "RandomX — same\nalgorithm as\nMonero"],
]
p_table = Table(principles, colWidths=[1.7*inch]*4)
p_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), QTC_DARK),
    ('BACKGROUND', (0,1), (-1,1), QTC_SILVER),
    ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
    ('TEXTCOLOR',  (0,1), (-1,1), HexColor('#334155')),
    ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTNAME',   (0,1), (-1,1), 'Helvetica'),
    ('FONTSIZE',   (0,0), (-1,0), 9),
    ('FONTSIZE',   (0,1), (-1,1), 8),
    ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING',    (0,0), (-1,-1), 10),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ('GRID',       (0,0), (-1,-1), 0.5, WHITE),
]))
elements.append(p_table)
elements.append(Spacer(1, 0.25*inch))
elements.append(HRFlowable(width="100%", thickness=1, color=QTC_ACCENT))
elements.append(Spacer(1, 0.1*inch))
elements.append(Paragraph("Version 2.0  |  April 2026  |  Cori Testnet Active", caption_style))
elements.append(Paragraph("Open Source  |  No Premine  |  Community Owned  |  github.com/Kstyle12/qubit-topcoin", caption_style))
elements.append(Spacer(1, 0.1*inch))
elements.append(HRFlowable(width="100%", thickness=1, color=QTC_ACCENT))
elements.append(PageBreak())

def section(title):
    elements.append(Spacer(1, 0.05*inch))
    elements.append(Paragraph(title, h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=QTC_LIGHT))
    elements.append(Spacer(1, 0.05*inch))

def subsection(title):
    elements.append(Paragraph(title, h2_style))

def body(text):
    elements.append(Paragraph(text, body_style))

# ABSTRACT
section("Abstract")
body("Qubit TopCoin (QTOP) is a decentralized, quantum-resistant cryptocurrency designed to be the logical successor to Bitcoin in a post-quantum world. Where existing cryptocurrencies rely on elliptic curve cryptography that is provably vulnerable to sufficiently advanced quantum computers, QTOP is built from its genesis block with FALCON-512 post-quantum signatures — a scheme standardized by the National Institute of Standards and Technology (NIST) in 2024. QTOP is not merely a faster or cheaper cryptocurrency. It is designed to be one of the most cryptographically secure stores of value ever created — hardened against threats that do not yet fully exist, so that the wealth held within it remains protected across decades of unpredictable technological change.")
body("Like Bitcoin's foundational vision of a purely peer-to-peer electronic cash system, QTOP operates without the need for trusted third parties, financial institutions, or centralized authorities of any kind. Every participant is equal. Every node matters. QTOP extends this vision further: not only removing the need for institutional trust, but removing the cryptographic vulnerabilities that threaten to undermine it entirely as quantum computing advances. Where Bitcoin is digital gold, QTOP is quantum-hardened digital gold — a long-term wealth storage asset built to remain secure not just for years, but for generations.")
body("QTOP combines this cryptographic foundation with the RandomX proof-of-work algorithm, ensuring that any person with a standard CPU is a first-class participant in securing the network. With a fixed supply of 21,000,000 QTOP, 2.5-minute block times, FALCON-512 node identity for post-quantum P2P authentication, and a halving schedule mirroring Bitcoin's proven economic model, Qubit TopCoin is designed to be the most accessible, secure, and future-proof store of value available to all people — equally — today.")

# SECTION 1
section("1. Introduction")
subsection("1.1 The Quantum Threat to Cryptography")
body("The security of nearly every major cryptocurrency in existence today — including Bitcoin and Ethereum — rests on the elliptic curve discrete logarithm problem. This assumption has held for decades. It will not hold forever. Quantum computers, leveraging Shor's algorithm, are capable of solving this problem exponentially faster than any classical machine, rendering every existing ECDSA-based wallet vulnerable to theft.")
body("Critically, the threat does not begin when quantum computers arrive. It begins now. An adversary can collect encrypted blockchain transactions today and decrypt them retroactively once quantum capability exists — a strategy known as 'harvest now, decrypt later.' Wallets that have ever exposed a public key on-chain are already at long-term risk.")

subsection("1.2 The Inadequacy of Existing Solutions")
body("The cryptocurrency ecosystem has been slow to respond. Bitcoin has no quantum-resistance upgrade path with community consensus. Ethereum's post-quantum roadmap remains years from implementation. Existing quantum-resistant projects suffer from stateful signature schemes, poor mining decentralization, and incomplete post-quantum implementation — most protect only transactions while leaving P2P node communication vulnerable.")

subsection("1.3 Qubit TopCoin")
body("Qubit TopCoin (QTOP) is built to fill that gap completely. It is not a patch applied to a vulnerable system. Every cryptographic primitive is post-quantum from the genesis block: FALCON-512 for transaction signatures, FALCON-512 for node identity and P2P authentication, and SHA-3 for all hashing operations. Mining uses RandomX — the same CPU-native algorithm that powers Monero — ensuring no ASIC advantage exists. QTOP is designed first and foremost as a long-term wealth storage asset whose security guarantees hold across the full time horizon over which wealth is stored.")

# SECTION 2
section("2. Technical Design")
subsection("2.1 Cryptographic Foundation — FALCON-512")
body("Qubit TopCoin uses FALCON-512 for all digital signatures — both transaction signing and node identity. FALCON-512 was standardized by NIST in 2024 as part of its Post-Quantum Cryptography Standardization Project. It derives its security from the Short Integer Solution problem over NTRU lattices, for which no efficient quantum algorithm is known.")

crypto_data = [
    ["Property", "ECDSA (Bitcoin)", "FALCON-512 (QTOP)"],
    ["Signature Size", "~71 bytes", "~690 bytes"],
    ["Public Key Size", "33 bytes", "897 bytes"],
    ["Quantum Resistant", "No", "Yes"],
    ["NIST Standardized", "No", "Yes (2024)"],
    ["Used For", "Transactions only", "Transactions + Node Identity"],
]
elements.append(make_table(crypto_data, [2.3*inch, 2.2*inch, 2.2*inch]))
elements.append(Spacer(1, 0.1*inch))

subsection("2.2 FALCON-512 Node Identity")
body("Every QTOP node generates a persistent FALCON-512 keypair on first startup, stored as its permanent network identity. This node identity is used to authenticate all peer-to-peer communications — not just transactions. When nodes connect, register peers, or broadcast blocks, their messages are signed with their FALCON-512 node key. This addresses a critical gap in existing quantum-resistant cryptocurrency designs, which typically protect only transaction signatures while leaving P2P networking vulnerable.")
body("Each node exposes its identity via the /identity API endpoint, allowing peers and users to verify the post-quantum authenticity of any node on the network. The node ID — a truncated SHA-3 hash of the node's public key — provides a human-readable identifier while the full 897-byte FALCON-512 public key provides cryptographic proof.")

subsection("2.3 Hashing — SHA-3")
body("All hashing operations in QTOP use SHA-3 (Keccak-256). While Bitcoin's SHA-256 is not directly broken by quantum computing, Grover's algorithm reduces its effective security from 256 bits to 128 bits against a quantum adversary. SHA-3 provides stronger quantum security margins and is the most current NIST-standardized hash function.")

subsection("2.4 Mining — RandomX")
body("Qubit TopCoin uses RandomX as its proof-of-work algorithm. RandomX was developed specifically to run most efficiently on general-purpose CPUs — the processors found in ordinary laptops and desktop computers. It executes random programs in a sandboxed virtual machine, requires large memory access patterns that map well to CPU cache architecture, and changes its program with each new block hash attempt. ASIC hardware provides no meaningful advantage over a standard CPU.")
body("The RandomX key rotates with every block based on the previous block's hash, making it impossible for specialized hardware to pre-compute solutions. A person mining QTOP on a three-year-old laptop competes on genuinely similar terms to a person running a rack of modern desktop CPUs. This is the core mechanism by which QTOP achieves and maintains decentralization.")

subsection("2.5 Integer Arithmetic — The Cori")
body("All amounts in the QTOP protocol are stored and processed as integers in units of cori — the smallest indivisible unit of QTOP. One QTOP equals exactly 100,000,000 cori. By using integer arithmetic throughout, QTOP eliminates the floating-point precision errors that plague prototype cryptocurrency implementations. This mirrors Bitcoin's use of satoshis and ensures that balances, fees, and rewards are always exact.")

elements.append(make_table([
    ["Unit", "Value", "Example"],
    ["1 cori", "0.00000001 QTOP", "Minimum transaction unit"],
    ["1 QTOP", "100,000,000 cori", "Standard unit"],
    ["Block reward", "5,000,000,000 cori", "50 QTOP per block"],
], [2.0*inch, 2.5*inch, 2.2*inch]))
elements.append(Spacer(1, 0.1*inch))

subsection("2.6 Block Structure")
body("Each QTOP block contains a SHA-3 header hash used as the block identifier, and a RandomX hash used as proof of work. This dual-hash design cleanly separates block identification from mining — the SHA-3 header hash feeds into RandomX, and the resulting RandomX hash must meet the difficulty target. Blocks are validated by checking both the SHA-3 header hash integrity and all FALCON-512 transaction signatures within.")

subsection("2.7 Block Time and Difficulty Adjustment")
body("QTOP targets a block time of 2.5 minutes. Mining difficulty adjusts automatically every 10 blocks based on actual vs expected block times, allowing the network to respond quickly to changes in mining participation. On a network with consistent mining activity, block times stabilize around the 2.5-minute target regardless of the number of miners.")

subsection("2.8 Peer-to-Peer Network")
body("QTOP operates as a fully decentralized peer-to-peer network. Nodes discover each other through DNS seed bootstrapping on first launch. Each node has a FALCON-512 identity keypair for post-quantum authenticated communication. The consensus mechanism is Nakamoto consensus — the chain with the greatest cumulative proof-of-work is the valid chain, enforced independently by every node.")

# SECTION 3
section("3. Tokenomics")
subsection("3.1 Fixed Supply")
body("Qubit TopCoin has a maximum supply of 21,000,000 QTOP. This cap is absolute and enforced at the protocol level. There is no premine, no developer allocation, no foundation reserve, and no initial coin offering. Every QTOP in existence is earned through proof-of-work mining, beginning at the genesis block. The first person to mine QTOP has the same advantage as the last: none, beyond the computational work they contribute.")

elements.append(Paragraph(
    '"Every QTOP in existence is earned through proof-of-work mining. No exceptions. No premine. No advantage."',
    quote_style))

subsection("3.2 Block Rewards and Halving")
body("The initial block reward is 50 QTOP (5,000,000,000 cori) per block. Every 210,000 blocks — approximately every 2.74 years at QTOP's 2.5-minute block time — the block reward is cut in half.")

halving_data = [
    ["Halving", "Block Height", "Approx. Year", "Block Reward"],
    ["Launch",    "0",         "2027", "50 QTOP"],
    ["1st",       "210,000",   "2030", "25 QTOP"],
    ["2nd",       "420,000",   "2032", "12.5 QTOP"],
    ["3rd",       "630,000",   "2035", "6.25 QTOP"],
    ["4th",       "840,000",   "2038", "3.125 QTOP"],
    ["Final",     "~6,930,000","~2109","0.00000001 QTOP"],
]
elements.append(make_table(halving_data, [1.5*inch, 1.5*inch, 1.7*inch, 2.0*inch]))
elements.append(Spacer(1, 0.1*inch))

subsection("3.3 Transaction Fees")
body("Every transaction includes a fee paid to the miner who includes it in a block. Fees are set freely by the sender and function as a market — during high demand, users offer higher fees for faster inclusion. In the long term, after all 21,000,000 QTOP have been mined, transaction fees become the sole miner compensation, sustaining network security indefinitely without inflation.")

subsection("3.4 No Inflation Mechanism")
body("There is no mechanism in the QTOP protocol to increase the 21,000,000 coin supply cap. No governance vote can change this. No developer key can authorize new minting. The supply schedule is enforced by consensus rules that every node validates independently.")

# SECTION 4
section("4. Network and Consensus")
subsection("4.1 Node Architecture")
body("QTOP nodes run on any consumer hardware. The production node is implemented in Rust using the actix-web framework, providing a REST API for wallets, miners, and peer nodes. Pruned nodes store approximately 20-30GB of chain data, stable long-term, ensuring that running a full validating node remains accessible to anyone with a standard laptop.")

node_data = [
    ["Node Type", "Storage", "Role", "Who Runs It"],
    ["Pruned (Default)", "~20-30GB", "Full validation, consensus", "Anyone with a laptop"],
    ["Archive (Optional)", "Grows over time", "Full history storage", "Exchanges, researchers"],
]
elements.append(make_table(node_data, [1.5*inch, 1.2*inch, 2.1*inch, 1.9*inch]))
elements.append(Spacer(1, 0.1*inch))

subsection("4.2 Consensus")
body("QTOP uses Nakamoto consensus. The valid chain is always the one representing the greatest cumulative proof-of-work. Every node independently validates every block and every transaction, trusting no one. Transactions are considered final after 6 confirmations — approximately 15 minutes at QTOP's 2.5-minute block time.")

subsection("4.3 REST API")
body("The QTOP node exposes a REST API for all network interactions:")

api_data = [
    ["Endpoint", "Method", "Description"],
    ["/status", "GET", "Node info, chain height, peers, difficulty"],
    ["/chain", "GET", "Full blockchain data"],
    ["/mine", "GET", "Mine pending transactions"],
    ["/identity", "GET", "Node FALCON-512 public key and ID"],
    ["/balance/{address}", "GET", "Wallet balance in cori and QTOP"],
    ["/transactions/new", "POST", "Submit signed transaction"],
    ["/peers/register", "POST", "Register peer node"],
    ["/peers/sync", "GET", "Sync with peer chains"],
]
elements.append(make_table(api_data, [1.8*inch, 0.8*inch, 4.1*inch]))
elements.append(Spacer(1, 0.1*inch))

# SECTION 5
section("5. Implementation")
subsection("5.1 Production Rust Node")
body("The QTOP production node is implemented in Rust — a memory-safe systems programming language that eliminates entire classes of vulnerabilities present in C and C++ implementations. The node compiles to a single binary with no runtime dependencies beyond the RandomX and FALCON-512 libraries.")

impl_data = [
    ["Module", "Purpose"],
    ["wallet.rs", "FALCON-512 keypair generation and address derivation"],
    ["transaction.rs", "Transaction signing, verification, and serialization"],
    ["block.rs", "RandomX proof-of-work mining and block validation"],
    ["blockchain.rs", "Chain management, rewards, difficulty adjustment"],
    ["storage.rs", "Persistent chain storage to disk"],
    ["sync.rs", "Peer chain synchronization and consensus"],
    ["identity.rs", "FALCON-512 node identity generation and signing"],
    ["discovery.rs", "Automatic peer discovery via DNS seeds"],
    ["node.rs", "actix-web REST API server"],
]
elements.append(make_table(impl_data, [1.8*inch, 4.9*inch]))
elements.append(Spacer(1, 0.1*inch))

subsection("5.2 Wallet Security")
body("QTOP wallets use AES-256-GCM encryption with PBKDF2 key derivation (480,000 iterations) to protect private keys. The wallet file stores the FALCON-512 public key and encrypted private key — the private key is never stored in plain text. Wallet addresses are derived from the FALCON-512 public key via SHA-3 hashing and Base58Check encoding, producing addresses beginning with recognizable prefixes.")

subsection("5.3 One-Command Installation")
body("Anyone can join the Cori Testnet with a single command that installs all dependencies, builds the node, and creates startup scripts automatically:")
body("curl -sSL https://raw.githubusercontent.com/Kstyle12/qubit-topcoin/main/install.sh | bash")
body("On Linux servers, a second command sets up the node as a permanent systemd service that starts automatically on boot and restarts if it crashes.")

# SECTION 6
section("6. Cori Testnet")
body("The Cori Testnet is QTOP's active test network, named after QTOP's smallest unit of account. It is the proving ground for the protocol before mainnet launch. The Cori Testnet is live and accepting connections. Anyone can join by running the one-command installer and connecting to a seed node.")
body("The Cori Testnet includes a live block explorer at explorer.html showing real-time block data, transaction details, node identity and FALCON-512 public key, RandomX mining confirmation, and address balance lookups.")

testnet_data = [
    ["Property", "Value"],
    ["Network Name", "Cori Testnet"],
    ["Status", "Active"],
    ["Genesis Block", "Mined with RandomX difficulty 2"],
    ["Mining", "Open — any CPU can participate"],
    ["Block Explorer", "Available at explorer.html"],
    ["Install", "One command — see install.sh"],
]
elements.append(make_table(testnet_data, [2.5*inch, 4.2*inch]))
elements.append(Spacer(1, 0.1*inch))

# SECTION 7
section("7. Roadmap")
body("The following roadmap represents QTOP's development timeline. All dates are targets. QTOP will not launch mainnet until the software has been independently reviewed for security.")

roadmap_data = [
    ["Phase", "Period", "Milestones"],
    ["Phase 1\nFoundation", "Q1-Q2 2026",
     "Whitepaper, Python prototype, Rust node, FALCON-512 node identity, RandomX mining, block explorer, one-command installer, Cori Testnet launch"],
    ["Phase 2\nTestnet", "Q3-Q4 2026",
     "Public cloud nodes, DNS seed infrastructure, community mining, security review, exchange pre-listing conversations"],
    ["Phase 3\nAudit", "Q1-Q2 2027",
     "Formal third-party security audit, findings addressed publicly, mainnet preparation"],
    ["Phase 4\nMainnet", "Q3 2027",
     "Security audit complete, mainnet genesis block mined, node software released, exchange listings"],
    ["Phase 5\nGrowth", "Q4 2027+",
     "Exchange listings, hardware wallet support, mobile wallets, institutional outreach"],
]
elements.append(make_table(roadmap_data, [1.1*inch, 1.0*inch, 4.6*inch]))
elements.append(Spacer(1, 0.1*inch))

# SECTION 8
section("8. Conclusion")
body("Bitcoin changed the world. For the first time in human history, people anywhere on earth could store and transfer value without asking permission from a bank, a government, or any institution at all. That idea — that money could belong to the people who hold it, secured by mathematics rather than by trust in authority — was revolutionary. It still is.")
body("But Bitcoin was built in 2008. The mathematical assumptions that secure it were sound then. They are becoming less sound every year. The quantum era is not a distant science fiction scenario — it is an engineering timeline, and that timeline is accelerating.")
body("QTOP is ready now. Built from its first line of code with full awareness of what is coming: FALCON-512 signatures that no quantum algorithm can break, RandomX mining that any CPU can compete in, integer arithmetic that eliminates precision errors, post-quantum node identity that secures P2P communication, and a fixed supply of 21,000,000 coins with no premine and no hidden advantage for anyone.")
body("This is not a project built for institutional investors, though they are welcome. It is built for the student, the farmer, the nurse, and the engineer in every country on earth who deserves access to a secure, decentralized, quantum-resistant store of value on equal terms with everyone else.")
body("Decentralization is not a feature of QTOP. It is the purpose of QTOP. A network that belongs to no one belongs to everyone. That is what QTOP is built to be.")
body("The quantum threat is real. The solution is here, it is open, and it is yours.")

elements.append(Spacer(1, 0.2*inch))
elements.append(HRFlowable(width="100%", thickness=2, color=QTC_ACCENT))
elements.append(Spacer(1, 0.15*inch))
elements.append(Paragraph("Qubit TopCoin. For everyone. Forever.", quote_style))
elements.append(Spacer(1, 0.15*inch))
elements.append(HRFlowable(width="100%", thickness=2, color=QTC_ACCENT))
elements.append(Spacer(1, 0.2*inch))

footer_data = [[
    Paragraph("Version 2.0\nApril 2026", caption_style),
    Paragraph("Ticker: QTOP\nMax Supply: 21,000,000", caption_style),
    Paragraph("Open Source\ngithub.com/Kstyle12/qubit-topcoin", caption_style),
    Paragraph("No Premine\nFair Launch", caption_style),
]]
footer_table = Table(footer_data, colWidths=[1.7*inch]*4)
footer_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), QTC_DARK),
    ('TEXTCOLOR',  (0,0), (-1,-1), WHITE),
    ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING',    (0,0), (-1,-1), 12),
    ('BOTTOMPADDING', (0,0), (-1,-1), 12),
]))
elements.append(footer_table)

doc.build(elements)
print("QTOP Whitepaper v2.0 generated successfully.")
