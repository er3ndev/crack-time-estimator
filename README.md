# ⏱️ crack-time-estimator

A Python tool that estimates how long it would take government agencies like the **NSA**, **FBI**, **GCHQ**, and others to brute-force your password — based on real-world GPU benchmarks and estimated institutional compute power.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/hashcat-benchmarks-red?style=for-the-badge" />
</p>

---

## 🔍 What It Does

1. **Analyzes your password** — charset, entropy, length, common pattern detection
2. **Estimates crack time** across **13 attacker profiles**, from a single GPU to the NSA's full capacity
3. **Supports 10 hash algorithms** — MD5, SHA-1, SHA-256, SHA-512, bcrypt, scrypt, Argon2, NTLM, WPA2
4. **Includes a quantum computer estimate** using Grover's algorithm (√N speedup)
5. **Gives actionable recommendations** to strengthen your password

> ⚠️ Your password is **never stored, logged, or transmitted**. Everything runs locally.

---

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/crack-time-estimator.git
cd crack-time-estimator
python password.py
```

No dependencies required — runs on **Python 3.8+** with only standard library modules.

---

## 📸 Example Output

```
══════════════════════════════════════════════════════════════
  📊 PASSWORD ANALYSIS
══════════════════════════════════════════════════════════════
  Password (masked) : K****************************I
  Length            : 30 characters
  Charset size      : 95 possible characters
  Entropy           : 197.10 bits
  Total keyspace    : 2.15e+59

  Strength Level:
    [████████████████████] EXCELLENT

══════════════════════════════════════════════════════════════
  ⏱️  CRACK TIME ESTIMATES — SHA-512
══════════════════════════════════════════════════════════════
  🏠 Home User                          7.5 GH/s   4.54 × 10^41 years
  💻 Small Hacker Group                60.0 GH/s   5.67 × 10^40 years
  🇨🇦 RCMP (Canada)                     1.9 TH/s   1.75 × 10^39 years
  🇬🇧 GCHQ (UK)                        56.2 TH/s   6.05 × 10^37 years
  🇺🇸 FBI (USA)                       168.8 TH/s   2.02 × 10^37 years
  🇺🇸 CIA (USA)                       600.0 TH/s   5.67 × 10^36 years
  🇺🇸 NSA (USA)                         7.5 PH/s   4.54 × 10^35 years
  ⚛️ Quantum Computer (~2035)          Grover's    1.47 × 10^16 years

  🌌 Even the NSA would need 32,857,449,275,934,473x the age
     of the universe to crack this password!
```

---

## 🏛️ Supported Organizations

| Organization | Country | Estimated GPU Cluster |
|---|---|---|
| 🏠 Home User | Individual | 1x RTX 4090 |
| 💻 Small Hacker Group | Anonymous | 8x RTX 4090 |
| 🏢 Mid-size Company | Corporate | 50x A100 |
| 🇨🇦 RCMP | Canada | 200 GPUs |
| 🇬🇧 GCHQ | United Kingdom | 5,000 GPUs + ASIC |
| 🇩🇪 BND | Germany | 3,000 GPUs |
| 🇮🇱 Unit 8200 | Israel | 8,000 GPUs |
| 🇷🇺 FSB | Russia | 10,000 GPUs |
| 🇨🇳 MSS | China | 50,000 GPUs |
| 🇺🇸 FBI | USA | 15,000 GPUs |
| 🇺🇸 CIA | USA | 50,000 GPUs |
| 🇺🇸 NSA | USA | 500,000 GPUs + custom ASICs |
| ⚛️ Quantum | Future (~2035) | Grover's Algorithm |

---

## 🔐 Supported Hash Algorithms

| Algorithm | Single GPU (RTX 4090) | Security Rating |
|---|---|---|
| MD5 | 164.0 GH/s | 🔴 Very Weak |
| NTLM | 300.0 GH/s | 🔴 Very Weak |
| SHA-1 | 56.0 GH/s | 🟠 Weak |
| SHA-256 | 22.0 GH/s | 🟡 Moderate |
| SHA-512 | 7.5 GH/s | 🟡 Moderate |
| scrypt | 3.2 MH/s | 🟢 Strong |
| WPA2 | 2.5 MH/s | 🟢 Strong |
| bcrypt (cost=10) | 184.0 KH/s | 🟢 Strong |
| bcrypt (cost=12) | 46.0 KH/s | 🔵 Very Strong |
| Argon2 | 1.5 KH/s | 🔵 Strongest |

> Hash rates sourced from [Hashcat benchmarks](https://hashcat.net/hashcat/) on NVIDIA RTX 4090 (2024).

---

## 📚 Methodology

- **Brute-force model**: Calculates total keyspace (`charset^length`) and divides by total hash rate. On average, half the keyspace needs to be searched.
- **GPU benchmarks**: Based on real Hashcat benchmarks on NVIDIA RTX 4090.
- **Institutional capacity**: Estimated from OSINT reports, government budget analyses, and known supercomputer specs. NSA estimates incorporate Snowden-era documents and academic research.
- **Quantum computing**: Uses Grover's algorithm which provides a quadratic (√N) speedup over classical brute-force. Estimated at 10⁶ iterations/sec for a future fault-tolerant quantum computer.

### ⚠️ Limitations

These estimates assume **pure brute-force attacks only**. Real-world attacks may be significantly faster due to:
- Dictionary / wordlist attacks
- Rainbow tables (for unsalted hashes)
- Rule-based mutations
- Social engineering
- Credential stuffing from data breaches

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
