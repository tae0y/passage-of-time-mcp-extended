# "Passage of Time" Model Context Protocol (MCP) Server 🕐

An MCP server that gives language models temporal awareness and time calculation abilities. Teaching LLMs the significance of the passage of time through collaborative tool development.

![Claude's Passage of Time Tools](docs/screenshot-0.png)

## 📖 The Story

This project emerged from a philosophical question: "Can AI perceive the passage of time?" What started as an exploration of machine consciousness became a practical solution to a real problem - LLMs can't reliably calculate time differences.

Instead of publishing a paper about how "silly" these models are at mental math, we decided to do what we've done for ourselves: **equip them with a calculator for time**.

Through human-LLM collaboration, we discovered that with proper temporal tools, models can uncover surprising insights about conversation patterns, work rhythms, and the human experience of time.

[Read the full story on Medium →](https://medium.com/@jeremie.lumbroso/teaching-ai-the-significance-of-the-passage-of-time-yes-that-one-106ad7d20957)

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- An MCP-compatible client (Claude.ai, Continue.dev, etc.)

### Installation

1. Clone the repository.

    ```bash
    git clone https://github.com/jlumbroso/passage-of-time-mcp.git
    cd passage-of-time-mcp
    ```

1. Install dependencies.

    ```bash
    uv sync
    ```

1. Run the server.

    ```bash
    uv run passage-of-time-mcp
    ```

The server will start on `http://0.0.0.0:8000/mcp` using the Streamable HTTP transport.

### Connecting to Claude.ai

1. In Claude.ai, go to **Settings** → **Integrations**.
1. Click **Add integration** and select **Custom**.
1. Enter the server URL: `https://your-server-domain/mcp`
1. Save and enable all the time-related tools.

> **Note:** For production deployment with Cloudflare Tunnel, see [docs/setup-cloudflare.md](docs/setup-cloudflare.md). For local development, you can use [ngrok](https://ngrok.com/) to expose `http://localhost:8000`.

## 🛠️ Available Tools

### Core Functions

#### `current_datetime(timezone="America/New_York")`
Returns the current date and time. The foundation of temporal awareness.

```
Returns: "2024-01-15 14:30:45 EST"
```

#### `time_difference(timestamp1, timestamp2, unit="auto")`
Calculates the duration between two timestamps with human-readable output.

```python
# Example response:
{
    "seconds": 11401,
    "formatted": "3 hours, 10 minutes, 1 second",
    "requested_unit": 3.17,  # if unit="hours"
    "is_negative": false
}
```

#### `timestamp_context(timestamp)`
Provides human context about a timestamp - is it weekend? Business hours? Dinner time?

```python
# Example response:
{
    "time_of_day": "evening",
    "day_of_week": "Saturday", 
    "is_weekend": true,
    "is_business_hours": false,
    "typical_activity": "leisure_time",
    "relative_day": "today"
}
```

#### `time_since(timestamp)`
Calculates how long ago something happened with contextual descriptions.

```python
# Example response:
{
    "seconds": 7200,
    "formatted": "2 hours ago",
    "context": "earlier today"
}
```

#### `parse_timestamp(timestamp)`
Converts timestamps between different formats for maximum compatibility.

```python
# Example response:
{
    "iso": "2024-01-15T14:30:45-05:00",
    "unix": "1705343445",
    "human": "January 15, 2024 at 2:30 PM EST",
    "day_of_week": "Monday"
}
```

#### `add_time(timestamp, duration, unit)`
Adds or subtracts time with natural language descriptions.

```python
# Example response:
{
    "result": "2024-01-16 14:30:45",
    "iso": "2024-01-16T14:30:45-05:00",
    "description": "tomorrow at 2:30 PM"
}
```

#### `format_duration(seconds, style="full")`
Formats durations in various styles for different contexts.

```python
# style="full": "2 hours, 30 minutes, 15 seconds"
# style="compact": "2h 30m 15s"
# style="minimal": "2:30:15"
```

## 💡 Example Conversations

### Basic Time Awareness
```
Human: What time is it?
Claude: [calls current_datetime] It's currently 3:45 PM EST on Monday, January 15, 2024.
```

### Conversation Rhythm Analysis
```
Human: Let's have a discussion about AI consciousness.
Claude: [calls current_datetime at start of each response]
[After several exchanges]
Human: What patterns do you notice in our conversation?
Claude: Looking at the timestamps, I notice you're taking 30 seconds to 2 minutes between responses, suggesting active engagement. The 3-minute pause before your question about implementation shows deeper consideration...
```

### Understanding Work Context
```
Human: [at 11:45 PM] Can you help me debug this code?
Claude: [calls current_datetime, then timestamp_context] 
I see it's late night on a weekday. Given that it's approaching midnight, let me help you efficiently so you can get some rest. Here's a focused debugging approach...
```

## 🏗️ Design Philosophy

This server embodies several key principles:

1. **Cognitive Partnership**: We treat LLMs as cognitive partners who need proper tools, not black boxes to be dressed up.

2. **Collaborative Design**: The tool suite emerged from asking Claude what they needed, not imposing our assumptions.

3. **Human Context Matters**: Time isn't just numbers - it's about understanding human rhythms, work patterns, and social contexts.

4. **Practical Over Perfect**: We provide the tools models actually need, tested through real conversations.

## 🔧 Configuration

### Timezone Support
The server defaults to `America/New_York` but supports all standard timezone names:
- `UTC`
- `US/Pacific` 
- `Europe/London`
- `Asia/Tokyo`
- etc.

### Timestamp Formats
All timestamps must use one of these formats:
- Full: `YYYY-MM-DD HH:MM:SS` (e.g., "2024-01-15 14:30:45")
- Date only: `YYYY-MM-DD` (e.g., "2024-01-15")

This strict formatting prevents ambiguity and ensures reliable calculations.

## 🚧 Known Issues & Future Work

### Current Limitations
- Server requires public URL for web-based clients
- No persistent memory of past time calculations

### Roadmap
- [x] Migrate to modern Streamable HTTP transport
- [x] Add Docker support for easier deployment
- [ ] Create browser extension for local development
- [ ] Add configurable activity patterns per user
- [ ] Support for calendar integration
- [ ] Natural language time parsing ("next Tuesday", "in 3 hours")

## 🤝 Contributing

This project emerged from human-LLM collaboration and welcomes more of the same! Whether you're contributing solo or with AI assistance, we value:

1. **Practical additions** - Tools that solve real temporal understanding problems
2. **Human context** - Features that help models understand how humans experience time
3. **Clear documentation** - Examples that show real-world usage

### Development Setup

```bash
git clone https://github.com/jlumbroso/passage-of-time-mcp.git
cd passage-of-time-mcp

# Install dependencies (including dev)
uv sync

# Run tests
uv run pytest

# Run server locally
uv run passage-of-time-mcp
```

The server starts on `http://0.0.0.0:8000/mcp`.

### Deployment

For production deployment with Docker and Cloudflare Tunnel, see the [Cloudflare Tunnel setup guide](docs/setup-cloudflare.md).

![Setting up the passage-of-time MCP server in Claude's interface - each tool comes with clear descriptions and permissions](docs/screenshot-5b.png)

## 📝 License

Mozilla Public License 2.0 - because good ideas should spread while staying open.

## 🙏 Acknowledgments

- Created through extended collaboration between [Jérémie Lumbroso](https://github.com/jlumbroso) and Claude Opus 4.0 (Anthropic)
- Inspired by the question: "Can AI perceive the passage of time?"
- Built on [FastMCP](https://github.com/fastmcp/fastmcp) framework
- Special thanks to the [Natural and Artificial Minds initiative](https://nam.ai.princeton.edu/) at Princeton University

## 📚 Further Reading

- [Teaching AI "The Significance of the Passage of Time" - Medium Article](https://medium.com/@jeremie.lumbroso/teaching-ai-the-significance-of-the-passage-of-time-yes-that-one-106ad7d20957)
- [We Can't Understand AI Using our Existing Vocabulary - Been Kim et al.](https://arxiv.org/abs/2502.07586)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)

---

*"We're not just building better LLM tools. We're teaching curious cognitive systems about what it means to be human—one timestamp at a time."*
