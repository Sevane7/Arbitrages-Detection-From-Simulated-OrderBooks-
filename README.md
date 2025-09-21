# Arbitrage Detection From Simulated OrderBooks

This project simulates multiple order books (`OrderBook`) across different exchanges and automatically detects **arbitrage opportunities** using the `Arbitrages` class.

---

## 🚀 Features

- Generate realistic order books (bids / asks) with random variations.
- Pretty-print order book views.
- Detect arbitrage opportunities:
  - Intra-exchange (within the same order book),
  - Inter-exchange (across different order books).
- Compute optimal tradable quantities and potential **P&L**.
- Display results in a structured DataFrame.

---

## 📂 Code Structure

- **`OrderBook`**
  - Simulates an order book with multiple price/quantity levels.
  - Can generate multiple order books for a given symbol.
  - Provides a string representation of bids/asks.

- **`Arbitrages`**
  - Compares order books to detect arbitrage opportunities.
  - Stores results in a list of `Results` objects.
  - Produces a summary table including:
    - Bid/ask prices,
    - Arbitrable quantities,
    - Total P&L.

- **`Results`**
  - A dataclass representing a single arbitrage opportunity.

---

## 📦 Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/Sevane7/Arbitrages-Detection-From-Simulated-OrderBooks-.git
cd Arbitrages-Detection-From-Simulated-OrderBooks-
