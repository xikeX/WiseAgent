
# WiseAgent

![License](https://img.shields.io/badge/License-MIT-blue.svg)

[中文](https://github.com/xikeX/WiseAgent/blob/main/README_zh.md)
## Overview
![架构](assets/architecture.png)

`WiseAgent` is an advanced framework designed around large-language for llm base agents, with the goal of uncovering the potential for continuous learning in individual agents and fostering co-evolutionary intelligence across multiple agents. It offers a comprehensive suite of features, including perception, planning, memory, execution, interactive environment management, and knowledge extraction from memory. This enables the development and deployment of agent communities that can adapt to changes and improve their performance over time.

## Features

- **Single-Agent Support**: Supports environments for both single and multiple agents, making it easy for developers to get started while also meeting the needs of complex scenarios.
- **Multi-Agent Support**: Facilitates interaction and collaboration among multiple agents, promoting knowledge sharing and strategy optimization between them.

- **Continuous Learning**: Agents can learn from their environment and continuously improve their strategies through interaction.
- **Scalability**: The framework is designed with scalability in mind, capable of handling a large number of agents and complex environments. It balances performance and resource consumption to achieve efficient multi-agent interactions.
- **Flexible Architecture**: The framework adopts a modular design, allowing developers to customize and extend agents and environments as needed. It provides rich interfaces and tools to facilitate secondary development by developers.

## Installation

To install `WiseAgent`, use pip:

```bash
pip install -e .
```

## Usage

1. Configure the model file `config/env.yaml`
    ```yaml
    LLM:
        type: Model type, example: "OpenAI"
        api_key: "Model API key"
        base_url: "Model base URL"
        model_name: "Model name"
        verbose: "Whether to print model output, example: True"

    EMBEDDING:
        illustration: "EMBEDDING is optional and can be omitted"
        type: Model type, example: "openai"
        api_key: "Model API key"
        base_url: "Model base URL"
        model_name: "Model name"


    ```

2. Below is a quick example to help you get started; this script can be found in `example/run_agent/run_engineer.py`.

    ```python
    from wiseagent.action.normal_action.write_code import WriteCodeAction
    from wiseagent.core.agent import Agent

    def get_user_input(engineer):
        while True:
            user_input = input("Please input your task:")
            if user_input == "exit":
                break
            # Let the agent perform actions based on user input
            engineer.ask(user_input)

    def main():
        # Create an agent
        engineer = Agent.from_default(name="Bob", description="Bob is an engineer")
        # Register an action/tool
        engineer.register_action(WriteCodeAction())
        # Start the agent
        engineer.life()
        # Get user input and execute actions
        get_user_input(engineer)
        
    if __name__ == "__main__":
        main()
    ```

3. Additionally, agents and actions can also be created via a `.yaml` configuration file.

    ```yaml
    name: "(Required) Name of the agent, example: Bob"
    description: "(Optional) Description of the agent"

    action_list:
    - "MethodPlanAction"
    - "List of behaviors, indicating behavior classes, where MethodPlanAction for planning behaviors is mandatory."
    - "Other behaviors include ArxivAction, WriteCodeAction, etc., which can be found in wiseagent\action\normal_action."

    life_schedule_config: "(Required) Execution mode, example: ReActLifeSchedule"
    ```
    Specific examples can be found in the `example` directory.

    ```python
    from wiseagent.core.agent import Agent

    def get_user_input(engineer):
        while True:
            user_input = input("Please input your task:")
            if user_input == "exit":
                break
            # Let the agent perform actions based on user input
            engineer.ask(user_input)
            
    def main():
        agent: Agent = Agent.from_yaml_file(yaml_file)
        # Start the agent
        agent.life()
        # Get user input and execute actions
        get_user_input(agent)

    if __name__ == "__main__":
        main()
    ```

4. start the agent web page and server

    server
    ```bash
    python wiseagent\server\server.py
    ```
    web page
    ```bash
    streamlit run wiseagent\web\web_page.py
    ```

## Demo
![架构](assets/demo.gif)

## Features

- **Agent and Action Management**: The framework allows for the creation and management of agents and actions, enabling developers to define and execute complex behaviors.
For more detailed usage examples and advanced usage, please refer to the [Documentation](#documentation).
## Documentation

For more developer documentation, please refer to the [Developer Documentation](#developer-documentation).

## Contributing

We welcome community contributions! If you would like to contribute code to WiseAgent, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make changes and commit (`git commit -am 'Add some feature'`).
4. Push to your branch (`git push origin feature/your-feature-name`).

## License

`WiseAgent` follows the MIT license. For more details, see the [LICENSE](LICENSE) file.

## Contact

If you have any questions or need support, feel free to contact us.

---
If you like this project, please give it a star!
```
