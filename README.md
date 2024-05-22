---

# NEA Engine 1.0.0 Open Beta Release

### Key Updates:
- Enhanced AI engine performance for faster and more efficient operation
- Improved AI model architecture, enabling more accurate and responsive agents
- Refined and optimized legacy LLM models to improve interaction quality
- Upgraded capabilities of AI agents to perform a broader range of tasks
- Comprehensive bug fixes and overall system improvements

---

## NEA Engine - Solana-Based AI Agent Framework

NEA is a robust, high-performance framework designed for the creation, evolution, and deployment of AI-powered agents in a decentralized, scalable ecosystem. Built on the Solana blockchain, NEA provides developers with the tools to create intelligent, autonomous agents capable of interacting with various decentralized applications. It seamlessly integrates cutting-edge AI models, smart contracts, and decentralized technologies, offering an efficient platform for deploying AI solutions across a range of industries.

By leveraging the power of Solana's high-throughput, low-latency blockchain, NEA allows the creation of intelligent agents that can trade, interact, and evolve within a secure and transparent environment. This enables decentralized AI-driven systems that are more efficient, scalable, and cost-effective than traditional alternatives.

---

## Official Contract Address and Development Funding

This project operates through a single, official smart contract address to maintain security and transparency. To ensure authenticity and avoid potential fraud, please interact only with the address provided below:

- **DEX**: [NEA on Dexscreener](https://dexscreener.com/solana/)  
- **Website**: [NEA LIVE](https://neagents.live/)  
- **Twitter**: [@NEAGENTS](https://x.com/neagents)  
- **Telegram**: [NEA Community](https://t.me/)

All development and ongoing maintenance are funded through the creator’s wallet associated with the NEA token. This ensures that funds are allocated directly toward furthering the NEA ecosystem's growth and sustainability.

---

## Why Choose NEA?

### Developer-Centric:
NEA is crafted with the developer in mind, offering tools and features that simplify complex workflows, accelerate development processes, and provide flexible solutions to meet diverse project needs.

### Open-Source and Transparent:
NEA is fully open-source, providing transparency into the codebase and offering developers the opportunity to contribute to its evolution. Community-driven development ensures continuous improvement and innovation.

### Versatility and Adaptability:
NEA's modular architecture is designed to accommodate a wide range of applications, from experimental startups to large-scale enterprise systems. Whether you are building decentralized finance (DeFi) applications, AI agents, or other blockchain-based projects, NEA adapts to your specific requirements.

---

## Core Features

### Performance Optimization
NEA is engineered to provide high-speed and resource-efficient solutions. Its architecture ensures that AI agents run smoothly even under heavy workloads, delivering fast, responsive, and reliable performance.

### Modular Architecture
The modular design of NEA allows developers to use only the components they need, optimizing resource consumption while maintaining flexibility and control. This modularity ensures that developers can create customized solutions that are lightweight and focused.

### Scalable Solutions
From small prototypes to large-scale enterprise applications, NEA is built to scale with your project. As your needs grow, NEA's decentralized and distributed architecture allows for seamless scaling without compromising performance or security.

### Security by Design
NEA places a strong emphasis on security, incorporating advanced encryption techniques, smart contract auditing, and decentralized governance to ensure that applications built on NEA are secure and resistant to malicious attacks or vulnerabilities.

### Extensible and Customizable
With NEA, developers can extend the platform’s functionality by adding custom plugins, libraries, and APIs. This extensibility makes it easy to tailor NEA to meet the specific needs of a project or organization, providing a high degree of flexibility in implementation.

---

## Getting Started

To start working with NEA, simply install the package via PyPi:

```bash
pip install nea-agents-py
```

Once the package is installed, you can begin by defining an agent and providing it with the necessary tools. Here’s an example of how to create an agent that retrieves information from the internet:

```python
from nea import CodeAgent, DuckDuckGoSearchTool, HfApiModel

# Create an agent with a search tool and AI model
agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=HfApiModel())

# Run the agent to perform a query
agent.run("Provide the prices of Solana and Bitcoin for March 2025")
```

---

## Contributing to NEA

NEA is an open-source project, and we welcome contributions from the developer community. If you would like to contribute, report a bug, or suggest an enhancement, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request for review.

Together, we can improve NEA and build an ecosystem of AI-powered agents.

---

## Evaluating Open Models for Agentic Workflows

NEA integrates leading open-source AI models, and we have benchmarked these models using a diverse set of challenges. For more information on the benchmarking process and to view the results, please refer to [this dataset](https://huggingface.co/datasets/m-ric/agents_medium_benchmark_2). This resource provides insight into how various models perform across different agentic tasks.

---

## Citation

If you use NEA in your academic research, publications, or projects, please cite it using the following BibTeX entry:

```bibtex
@Misc{nea,
  title =        {NEA: A High-Performance Framework for Building Efficient Solana-Based Agentic Systems},
  author =       {Network Evolved Agents Inc.},
  howpublished = {\url{https://github.com/NEAGENTS/NEA}},
  year =         {2025}
}
```

--- 