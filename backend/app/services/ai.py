"""Simulated GenAI service for question answering.

This simulates the behavior of an LLM by generating contextual, structured
responses based on the question topic and selected learning mode. In production,
this would be replaced with a real LLM API call (e.g. Gemini, OpenAI, etc.).
"""
import random
import time

# Topic-based knowledge banks for simulation
_KNOWLEDGE_BANK = {
    "react": {
        "keywords": ["react", "component", "state", "props", "hook", "jsx", "virtual dom", "useState", "useEffect", "redux"],
        "simple": [
            "React is a JavaScript library for building user interfaces. It works by breaking your UI into small, reusable **components** — think of them like LEGO bricks that you assemble to build your page.\n\n**Key concepts:**\n- **Components**: Functions that return UI (JSX)\n- **State**: Data that can change and triggers re-renders\n- **Props**: Data passed from parent to child components\n- **Hooks**: Functions like `useState` and `useEffect` to add state/side-effects to functional components",
            "React uses a **Virtual DOM** to efficiently update the browser. When state changes, React compares the old and new virtual DOM, then only updates the actual DOM where changes occurred — this is called **reconciliation**.\n\nState in React is managed with `useState`:\n```js\nconst [count, setCount] = useState(0);\n```\nWhen `setCount` is called, React re-renders the component with the new value.",
        ],
        "example": [
            "Here's a simple React counter component:\n\n```jsx\nimport { useState } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n\n  return (\n    <div>\n      <p>You clicked {count} times</p>\n      <button onClick={() => setCount(count + 1)}>\n        Click me!\n      </button>\n    </div>\n  );\n}\n```\n\nEvery time the button is clicked, `setCount` updates the state and React re-renders the component with the new count value.",
            "A real-world example: a **Todo App** with React\n\n```jsx\nfunction TodoApp() {\n  const [todos, setTodos] = useState([]);\n  const [input, setInput] = useState('');\n\n  const addTodo = () => {\n    setTodos([...todos, { id: Date.now(), text: input }]);\n    setInput('');\n  };\n\n  return (\n    <div>\n      <input value={input} onChange={e => setInput(e.target.value)} />\n      <button onClick={addTodo}>Add</button>\n      <ul>{todos.map(t => <li key={t.id}>{t.text}</li>)}</ul>\n    </div>\n  );\n}\n```",
        ],
        "quiz": [
            "**Quiz: React Fundamentals** 🎯\n\n**Q1:** What hook is used to add state to a functional component?\n- A) `useContext`\n- B) `useState` ✅\n- C) `useRef`\n- D) `useMemo`\n\n**Q2:** What does the Virtual DOM do?\n→ It's a lightweight copy of the real DOM. React uses it to batch and minimize actual DOM updates for better performance.\n\n**Q3:** What are props?\n→ Props (properties) are read-only data passed from a parent component to a child component.\n\n**Try this:** Create a component that accepts a `name` prop and displays 'Hello, {name}!'",
        ],
    },
    "photosynthesis": {
        "keywords": ["photosynthesis", "plant", "chlorophyll", "sunlight", "glucose", "oxygen", "carbon dioxide", "chloroplast", "biology"],
        "simple": [
            "**Photosynthesis** is the process plants use to make their own food using sunlight. Think of it as a plant's cooking recipe:\n\n🌱 **Ingredients needed:**\n- Sunlight (energy)\n- Water (H₂O) — absorbed through roots\n- Carbon dioxide (CO₂) — absorbed through tiny pores called stomata\n\n🍽️ **Products made:**\n- Glucose (C₆H₁₂O₆) — the plant's food/energy\n- Oxygen (O₂) — released into the air (which we breathe!)\n\n**The equation:**\n`6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂`",
            "Photosynthesis happens in two main stages inside the **chloroplast** (the green parts of plant cells):\n\n**1. Light-dependent reactions** (in the thylakoid membrane)\n- Sunlight splits water molecules\n- Produces ATP and NADPH (energy carriers)\n- Releases oxygen as a byproduct\n\n**2. Calvin Cycle / Light-independent reactions** (in the stroma)\n- Uses ATP and NADPH to convert CO₂ into glucose\n- Does NOT require direct light",
        ],
        "example": [
            "**Real-life example of photosynthesis:**\n\nImagine a leaf on a sunny day:\n1. Sunlight hits the **chlorophyll** pigments (which give leaves their green color)\n2. The plant draws up water through its roots and stem\n3. CO₂ enters through tiny holes called **stomata** (like tiny mouths on the leaf)\n4. Inside the **chloroplasts**, all three ingredients combine\n5. The plant produces **glucose** to grow and **oxygen** is released\n\n🌳 A single large tree can produce ~100 kg of oxygen per year and absorb 22 kg of CO₂ — enough oxygen for two people to breathe for a year!",
        ],
        "quiz": [
            "**Quiz: Photosynthesis** 🌿\n\n**Q1:** Where does photosynthesis take place?\n- A) Mitochondria\n- B) Nucleus\n- C) Chloroplast ✅\n- D) Ribosome\n\n**Q2:** What are the two raw materials (inputs) for photosynthesis?\n→ **Carbon dioxide (CO₂)** and **Water (H₂O)**\n\n**Q3:** What gas is released as a byproduct of photosynthesis?\n→ **Oxygen (O₂)**\n\n**Q4:** What is the green pigment in plants that captures sunlight?\n→ **Chlorophyll**\n\n**Bonus:** Why do leaves change color in autumn?\n→ Chlorophyll breaks down, revealing yellow/orange pigments that were always there!",
        ],
    },
    "water cycle": {
        "keywords": ["water cycle", "evaporation", "condensation", "precipitation", "transpiration", "runoff", "groundwater", "hydrological"],
        "simple": [
            "The **water cycle** (also called the hydrological cycle) describes how water continuously moves through Earth's systems:\n\n1. 🌊 **Evaporation**: Heat from the sun causes water from oceans, lakes, and rivers to turn into water vapor and rise\n2. 🌿 **Transpiration**: Plants release water vapor through their leaves\n3. ☁️ **Condensation**: As water vapor rises and cools, it forms clouds (tiny water droplets around dust particles)\n4. 🌧️ **Precipitation**: Water falls back to Earth as rain, snow, sleet, or hail\n5. 🏔️ **Collection**: Water flows into rivers, lakes, or soaks into the ground (groundwater)\n6. Back to step 1! The cycle repeats endlessly.",
        ],
        "example": [
            "**Tracking a single water molecule through the cycle:**\n\n💧 Your water molecule starts in the **Pacific Ocean**\n→ The sun heats it, and it **evaporates** into the atmosphere\n→ It rises high where it's cold and **condenses** around a dust particle, forming part of a cloud\n→ The cloud gets heavy and **precipitation** occurs — your molecule falls as rain in the Rocky Mountains\n→ It soaks into the ground (**infiltration**) or flows as **runoff** into the Colorado River\n→ It flows to the ocean... and the cycle begins again!\n\n⏱️ A water molecule may spend 9 days in the atmosphere, 10 years in a lake, or 10,000 years in a glacier!",
        ],
        "quiz": [
            "**Quiz: The Water Cycle** 💧\n\n**Q1:** What process turns liquid water into water vapor?\n- A) Condensation\n- B) Precipitation\n- C) Evaporation ✅\n- D) Infiltration\n\n**Q2:** What is transpiration?\n→ The process by which plants release water vapor through their leaves\n\n**Q3:** What causes water vapor to form clouds?\n→ **Condensation** — water vapor cools and condenses around tiny particles\n\n**Q4:** Name three forms of precipitation:\n→ Rain, Snow, Hail (also: sleet, freezing rain)\n\n**Q5:** What happens to precipitation that doesn't flow into rivers?\n→ It either soaks into the ground (infiltration → groundwater) or evaporates again",
        ],
    },
    "machine learning": {
        "keywords": ["machine learning", "ml", "neural network", "deep learning", "training", "model", "algorithm", "classification", "regression", "ai", "artificial intelligence"],
        "simple": [
            "**Machine Learning (ML)** is a type of AI where computers learn from data instead of being explicitly programmed with rules.\n\n**Three main types:**\n\n1. 🎓 **Supervised Learning**: The algorithm learns from labeled examples (e.g., thousands of cat/dog photos labeled correctly) → learns to classify new photos\n\n2. 🔍 **Unsupervised Learning**: The algorithm finds patterns in unlabeled data (e.g., grouping customers by behavior)\n\n3. 🎮 **Reinforcement Learning**: An agent learns by trial and error with rewards/penalties (e.g., how game-playing AIs learn)\n\n**Common algorithms:** Linear Regression, Decision Trees, Neural Networks, SVM, K-Means",
        ],
        "example": [
            "**Real-world ML example: Email Spam Detection**\n\n1. **Data collection**: Gather 10,000 emails labeled 'spam' or 'not spam'\n2. **Feature extraction**: Count word frequencies ('free', 'prize', 'click here' appear more in spam)\n3. **Training**: Feed features + labels to a model (e.g., Naive Bayes classifier)\n4. **The model learns**: 'free' + 'prize' + 'urgent' → high probability of spam\n5. **Prediction**: New email arrives → model scores it → routes to spam folder\n6. **Feedback loop**: User corrections improve the model over time\n\nThis same pattern applies to Netflix recommendations, medical diagnosis, fraud detection, and more!",
        ],
        "quiz": [
            "**Quiz: Machine Learning** 🤖\n\n**Q1:** Which ML type uses labeled training data?\n- A) Unsupervised Learning\n- B) Supervised Learning ✅\n- C) Reinforcement Learning\n- D) Transfer Learning\n\n**Q2:** What is overfitting?\n→ When a model learns training data too well (including noise) and performs poorly on new, unseen data\n\n**Q3:** What is a neural network inspired by?\n→ The structure of the human brain — interconnected nodes (neurons) organized in layers\n\n**Q4:** What is the difference between classification and regression?\n→ **Classification** predicts a category (spam/not spam)\n→ **Regression** predicts a continuous value (house price)\n\n**Q5:** What is a training/test split?\n→ Dividing data into training data (to learn from) and test data (to evaluate performance on unseen examples)",
        ],
    },
    "default": {
        "simple": [
            "That's a great question! Let me break this down for you in simple terms.\n\nWhen approaching a new concept like this, it helps to start with the **core idea** — what is the fundamental thing this concept is trying to explain or solve?\n\nFrom your question, I can see you're exploring an interesting topic. Here are some key principles to keep in mind as you study:\n\n1. **Start with the 'why'** — Understanding why something works the way it does is more powerful than memorizing facts\n2. **Look for patterns** — Most concepts connect to things you already know\n3. **Practice with examples** — Try applying the concept to a real situation\n\nWould you like me to dive deeper into any specific aspect of this topic?",
            "Great question! Here's a structured way to think about this:\n\n**Foundation**: Every complex topic can be broken down into simpler building blocks. Start by identifying the core terminology and definitions.\n\n**Context**: Consider *when* and *why* this concept is used. Understanding the problem it solves makes it much easier to remember.\n\n**Connections**: How does this relate to other things you know? Knowledge forms a web — stronger connections mean better retention.\n\n💡 **Study tip**: Try teaching this concept to someone else (or even to yourself out loud). If you can explain it simply, you truly understand it!",
        ],
        "example": [
            "The best way to understand any concept is through a concrete example. Let me illustrate this with a relatable scenario:\n\nImagine you're learning a new concept for the first time. The most effective approach is:\n\n1. **Read** a concise explanation (like the ones I can provide!)\n2. **See** a worked example that shows the concept in action\n3. **Do** — try applying it yourself with a slightly different scenario\n4. **Teach** — explain it to someone else to solidify your understanding\n\nThis 'Read-See-Do-Teach' cycle is backed by cognitive science research on how humans best retain information. Would you like me to walk through a specific example for your topic?",
        ],
        "quiz": [
            "**Knowledge Check Time!** 🎯\n\nBefore I quiz you, let me make sure you have the core concepts down:\n\n**Key points to remember:**\n- ✅ Start with definitions and core principles\n- ✅ Understand *why* the concept exists\n- ✅ Connect it to real-world applications\n- ✅ Practice with varied examples\n\n**Self-assessment questions:**\n1. Can you define the main concept in one sentence?\n2. Can you give a real-world example of where it applies?\n3. What are the key components or steps involved?\n4. How does this connect to related topics you know?\n\nTry answering these in your head or write them down — active recall is one of the most powerful study techniques! 📚",
        ],
    },
}


def _detect_topic(question: str) -> str:
    """Detect the topic of the question from the knowledge bank."""
    question_lower = question.lower()
    for topic, data in _KNOWLEDGE_BANK.items():
        if topic == "default":
            continue
        keywords = data.get("keywords", [])
        if any(kw in question_lower for kw in keywords):
            return topic
    return "default"


def _get_mode_prefix(mode: str, topic: str) -> str:
    """Get a contextual prefix based on learning mode."""
    prefixes = {
        "simple": f"Here's a clear, simple explanation",
        "example": f"Let me show you a concrete example",
        "quiz": f"Let's test your knowledge",
    }
    return prefixes.get(mode, prefixes["simple"])


def generate_ai_answer(question: str, mode: str, user_notes: list[str] | None = None) -> dict:
    """
    Simulate a GenAI response.
    
    In a real implementation, this would:
    1. Embed the question using an embedding model
    2. Search user's notes/documents for relevant context (RAG)
    3. Send the question + context to an LLM API
    4. Return the streaming response
    
    For now, we simulate this with a knowledge bank and intelligent templating.
    """
    # Simulate processing time (like a real LLM)
    time.sleep(random.uniform(0.8, 1.8))
    
    topic = _detect_topic(question)
    topic_data = _KNOWLEDGE_BANK[topic]
    
    # Get responses for this mode
    mode_responses = topic_data.get(mode, topic_data.get("simple", []))
    if not mode_responses:
        mode_responses = _KNOWLEDGE_BANK["default"].get(mode, _KNOWLEDGE_BANK["default"]["simple"])
    
    base_answer = random.choice(mode_responses)
    
    # If user has notes, reference them
    notes_context = ""
    if user_notes and len(user_notes) > 0:
        notes_context = f"\n\n---\n📚 **From your study notes:**\nI found {len(user_notes)} relevant note(s) in your collection. Your notes show you've been studying related material — keep building on that foundation!"
    
    answer = base_answer + notes_context
    
    # Add mode-specific footer
    footers = {
        "simple": "\n\n---\n*💡 Want to see a concrete example? Switch to **Example** mode and ask again!*",
        "example": "\n\n---\n*🎯 Ready to test your understanding? Switch to **Quiz** mode!*",
        "quiz": "\n\n---\n*📖 Need a clearer explanation first? Switch to **Explain simply** mode!*",
    }
    answer += footers.get(mode, "")
    
    return {
        "answer": answer,
        "topic_detected": topic,
        "mode": mode,
        "sources": ["StudyMate Knowledge Base", "Your Study Notes"] if user_notes else ["StudyMate Knowledge Base"],
    }
