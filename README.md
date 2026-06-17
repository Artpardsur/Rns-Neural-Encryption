# Lightweight Post-Quantum Encryption for Neural Networks Based on RNS

[![AISMA 2026](https://img.shields.io/badge/AISMA-2026-blue)](https://ncfu.ru)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![C++17](https://img.shields.io/badge/C++-17-blue.svg)](https://isocpp.org/)

This repository contains the source code for the paper:

> **"Development of a Post-Quantum Encryption Algorithm for Neural Networks Based on Modular Codes"**  
> *AISMA-2026: International Workshop on Advanced Information Security Management and Applications*

---

## 📋 Overview

This project implements a **lightweight encryption method for neural network weights** using the **Residue Number System (RNS)** with inherent post-quantum resistance. The method allows linear computations to be performed **directly on encrypted data** without decryption, achieving:

- **100% accuracy** of the decrypted result
- **>7,000× speedup** in inference compared to Paillier homomorphic encryption
- **>8× total speedup** (including encryption and decryption)

The method uses modular coding with five moduli `{1009, 1013, 1019, 1021, 1031}` and two redundant moduli for error detection and correction.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Neural Network Weights                      │
│                         (float)                                │
└─────────────────────┬───────────────────────────────────────────┘
                      ▼
              ┌───────────────┐
              │  Quantization │  Q = 10000
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │  RNS Encoding │  moduli: 1009,1013,1019,1021,1031
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │  Encrypted    │  residues (5 numbers)
              │  Inference   │  dot product in encrypted domain
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │  Decryption  │  CRT + interval correction (L)
              └───────┬───────┘
                      ▼
              ┌───────────────┐
              │  Result       │  100% accuracy
              └───────────────┘
```

---

## 🔧 Requirements

### C++ (for encryption)
- GCC 7+ or Clang 5+
- CMake 3.10+ (optional)
- C++11 standard

### Python (for experiment and comparison)
- Python 3.10+
- NumPy
- scikit-learn
- matplotlib
- phe (Paillier encryption)
- tenseal (BFV comparison)

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/rns-neural-encryption.git
cd rns-neural-encryption
```

### 2. Compile C++ encryptor

```bash
g++ -o rns_encryptor src/cpp/rns_encryptor.cpp -std=c++11 -static
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the experiment

```bash
python src/python/rns_experiment.py
```

---

## 📊 Results

| Metric | Proposed (RNS) | Paillier |
|--------|----------------|----------|
| Encryption time (s) | 0.839 | 2.874 |
| Inference time (s) | **0.000038** | 0.271 |
| Decryption time (s) | 0.000011 | 0.030 |
| Speedup (inference) | **>7,000×** | 1× |
| Total speedup | **>8×** | 1× |
| Accuracy | **100%** | 100% |

> See the paper for full experimental details and comparison with BFV.

---

## 📁 Repository Structure

```
rns-neural-encryption/
├── README.md
├── LICENSE
├── requirements.txt
├── src/
│   ├── cpp/
│   │   ├── rns_encryptor.cpp    # C++ encryption core
│   │   └── CMakeLists.txt       # CMake build file
│   └── python/
│       ├── rns_experiment.py    # Main experiment script
│       └── rns_final.py         # Final version with full comparison
├── data/                        # Dataset (auto-downloaded)
├── results/                     # Experiment outputs (graphs)
└── docs/
    └── figures/                 # Paper figures
```

---

## 📖 Citation

If you use this code in your research, please cite our paper:

```bibtex
@inproceedings{Lidzhiev2026RNS,
  author    = {Lidzhiev, A.B. and Kalmykov, I.A. and Peleshenko, T.A. and Gish, A.S.},
  title     = {Development of a Post-Quantum Encryption Algorithm for Neural Networks Based on Modular Codes},
  booktitle = {AISMA-2026: International Workshop on Advanced Information Security Management and Applications},
  year      = {2026},
  publisher = {Springer},
  series    = {Lecture Notes in Networks and Systems}
}
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

This code is provided for reproducibility of the paper results. For questions or suggestions, please open an issue or contact the authors.

---

## 📧 Contact

**Artem B. Lidzhiev**  
[artemlidzhiev.4444@gmail.com](mailto:artemlidzhiev.4444@gmail.com)  
North Caucasus Federal University, Stavropol, Russia