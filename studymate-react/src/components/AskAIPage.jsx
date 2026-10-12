import { useEffect, useRef, useState } from "react";
import { apiRequest } from "../lib/api";

const starterPrompts = [
    "Explain React state in simple terms",
    "How does photosynthesis work?",
    "Quiz me on the water cycle",
    "Give me an example of machine learning"
];

const learningModes = [
    { id: "simple", label: "Explain simply", icon: "☼" },
    { id: "example", label: "Give an example", icon: "⌘" },
    { id: "quiz", label: "Quiz me", icon: "✎" }
];

const WELCOME_MESSAGE = "👋 Hi! I'm your **StudyMate AI Guide**. Ask me anything you're studying — I can explain concepts simply, give real-world examples, or quiz you on topics.\n\nTry one of the starter prompts below, or type your own question!";

/** Render markdown-like formatting: bold, code blocks, line breaks, bullets */
function RichText({ text }) {
    if (!text) return null;

    const lines = text.split("\n");
    const elements = [];
    let codeBlock = [];
    let inCode = false;

    lines.forEach((line, idx) => {
        if (line.startsWith("```")) {
            if (inCode) {
                elements.push(
                    <pre key={`code-${idx}`} className="ai-code-block">
                        <code>{codeBlock.join("\n")}</code>
                    </pre>
                );
                codeBlock = [];
                inCode = false;
            } else {
                inCode = true;
            }
            return;
        }
        if (inCode) {
            codeBlock.push(line);
            return;
        }

        // Render inline bold (**text**) and inline code (`text`)
        function renderInline(str) {
            const parts = str.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
            return parts.map((part, i) => {
                if (part.startsWith("**") && part.endsWith("**")) {
                    return <strong key={i}>{part.slice(2, -2)}</strong>;
                }
                if (part.startsWith("`") && part.endsWith("`")) {
                    return <code key={i} className="ai-inline-code">{part.slice(1, -1)}</code>;
                }
                return part;
            });
        }

        if (line.startsWith("---")) {
            elements.push(<hr key={`hr-${idx}`} className="ai-divider" />);
        } else if (line.startsWith("# ")) {
            elements.push(<h3 key={idx} className="ai-h3">{renderInline(line.slice(2))}</h3>);
        } else if (line.startsWith("## ") || line.startsWith("### ")) {
            const level = line.startsWith("### ") ? 4 : 3;
            const content = line.replace(/^#+\s/, "");
            elements.push(<h4 key={idx} className={`ai-h${level}`}>{renderInline(content)}</h4>);
        } else if (line.match(/^[-*•] /)) {
            elements.push(
                <li key={idx} className="ai-list-item">{renderInline(line.replace(/^[-*•] /, ""))}</li>
            );
        } else if (line.match(/^\d+\. /)) {
            elements.push(
                <li key={idx} className="ai-list-item ai-ordered">{renderInline(line.replace(/^\d+\. /, ""))}</li>
            );
        } else if (line.trim() === "") {
            elements.push(<br key={idx} />);
        } else if (line.startsWith("*") && line.endsWith("*") && !line.startsWith("**")) {
            elements.push(<p key={idx} className="ai-italic"><em>{renderInline(line.slice(1, -1))}</em></p>);
        } else {
            elements.push(<p key={idx} className="ai-para">{renderInline(line)}</p>);
        }
    });

    return <div className="ai-rich-text">{elements}</div>;
}

function AskAIPage({ token }) {
    const [messages, setMessages] = useState([
        {
            id: 1,
            role: "assistant",
            text: WELCOME_MESSAGE
        }
    ]);
    const [question, setQuestion] = useState("");
    const [mode, setMode] = useState("simple");
    const [isThinking, setIsThinking] = useState(false);
    const [feedback, setFeedback] = useState({});
    const [sessionId, setSessionId] = useState(null);
    const [showSources, setShowSources] = useState({});
    const inputRef = useRef(null);
    const conversationRef = useRef(null);
    const nextMessageId = useRef(2);

    useEffect(() => {
        if (conversationRef.current) {
            conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
        }
    }, [messages, isThinking]);

    function sendMessage(messageText = question) {
        const trimmedQuestion = messageText.trim();
        if (!trimmedQuestion || isThinking) {
            return;
        }

        const userMessage = {
            id: nextMessageId.current++,
            role: "user",
            text: trimmedQuestion
        };

        setMessages((currentMessages) => [...currentMessages, userMessage]);
        setQuestion("");
        setIsThinking(true);

        if (!token) {
            // Demo mode: show a helpful nudge
            setTimeout(() => {
                const demoMsg = {
                    id: nextMessageId.current++,
                    role: "assistant",
                    text: "🔒 **Sign in required**\n\nTo get AI answers, please sign in or create a free account in the **My Notes** section above.\n\nYour account lets you:\n- 💬 Get AI-powered answers to your study questions\n- 📝 Save and organize your notes\n- 🔍 Search your notes with AI context",
                    unavailable: false,
                };
                setMessages((cur) => [...cur, demoMsg]);
                setIsThinking(false);
            }, 600);
            return;
        }

        apiRequest("/ai/ask", {
            token,
            method: "POST",
            body: JSON.stringify({
                question: trimmedQuestion,
                mode,
                session_id: sessionId,
            })
        }).then((answer) => {
            if (answer.session_id && !sessionId) {
                setSessionId(answer.session_id);
            }
            const assistantMessage = {
                id: nextMessageId.current++,
                role: "assistant",
                text: answer.answer || "The AI service returned no answer.",
                sources: answer.sources,
                topic: answer.topic_detected,
            };
            setMessages((currentMessages) => [
                ...currentMessages,
                assistantMessage
            ]);
        }).catch((requestError) => {
            const assistantMessage = {
                id: nextMessageId.current++,
                role: "assistant",
                unavailable: true,
                text: requestError.message || "Something went wrong. Please try again.",
            };
            setMessages((currentMessages) => [
                ...currentMessages,
                assistantMessage
            ]);
        }).finally(() => {
            setIsThinking(false);
        });
    }

    function startNewChat() {
        setMessages([{
            id: nextMessageId.current++,
            role: "assistant",
            text: WELCOME_MESSAGE,
        }]);
        setQuestion("");
        setFeedback({});
        setIsThinking(false);
        setSessionId(null);
        setShowSources({});
        inputRef.current?.focus();
    }

    const modeLabel = learningModes.find((m) => m.id === mode)?.label || mode;

    return (
        <section className="content-page ai-page" id="ask-ai">
            <section className="ai-heading">
                <div>
                    <p className="section-label">YOUR STUDY COMPANION</p>
                    <h1>Ask AI about your doubts</h1>
                    <p>
                        Explore a concept at your pace. Ask for a simple
                        explanation, an example, or a quick knowledge check.
                    </p>
                </div>
                <div className="ai-status">
                    <span className="ai-status-dot" />
                    {token ? "AI Ready" : "Sign in to chat"}
                </div>
            </section>

            <section className="chat-panel" aria-label="Study question chat">
                <div className="chat-topbar">
                    <div className="chat-assistant">
                        <span className="chat-avatar" aria-hidden="true">✦</span>
                        <div>
                            <strong>StudyMate Guide</strong>
                            <span><i /> {token ? `Mode: ${modeLabel}` : "Ready to help you learn"}</span>
                        </div>
                    </div>
                    <button
                        type="button"
                        className="new-chat-btn"
                        onClick={startNewChat}
                    >
                        <span aria-hidden="true">↻</span> New chat
                    </button>
                </div>

                <div className="conversation" ref={conversationRef} aria-live="polite">
                    {messages.map((message) => (
                        <article
                            className={`chat-message ${message.role}${message.unavailable ? " unavailable" : ""}`}
                            key={message.id}
                        >
                            {message.role === "assistant" && (
                                <span className="message-avatar" aria-hidden="true">S</span>
                            )}
                            <div className="message-content">
                                <RichText text={message.text} />

                                {/* Sources badge */}
                                {message.sources && message.sources.length > 0 && (
                                    <div className="message-sources">
                                        <button
                                            type="button"
                                            className="sources-toggle"
                                            onClick={() => setShowSources((cur) => ({
                                                ...cur,
                                                [message.id]: !cur[message.id]
                                            }))}
                                        >
                                            📚 {message.sources.length} source{message.sources.length !== 1 ? "s" : ""}
                                            {showSources[message.id] ? " ▲" : " ▼"}
                                        </button>
                                        {showSources[message.id] && (
                                            <ul className="sources-list">
                                                {message.sources.map((src, i) => (
                                                    <li key={i}>{src}</li>
                                                ))}
                                            </ul>
                                        )}
                                    </div>
                                )}

                                {/* Feedback */}
                                {message.role === "assistant" && message.id !== 1 && !message.unavailable && (
                                    <div className="message-feedback" aria-label="Rate this answer">
                                        <span>Helpful?</span>
                                        <button
                                            type="button"
                                            className={feedback[message.id] === "yes" ? "selected" : ""}
                                            onClick={() => setFeedback((current) => ({
                                                ...current,
                                                [message.id]: "yes"
                                            }))}
                                            aria-label="This answer was helpful"
                                        >
                                            👍
                                        </button>
                                        <button
                                            type="button"
                                            className={feedback[message.id] === "no" ? "selected" : ""}
                                            onClick={() => setFeedback((current) => ({
                                                ...current,
                                                [message.id]: "no"
                                            }))}
                                            aria-label="This answer was not helpful"
                                        >
                                            👎
                                        </button>
                                    </div>
                                )}
                            </div>
                        </article>
                    ))}

                    {isThinking && (
                        <div className="chat-message assistant">
                            <span className="message-avatar" aria-hidden="true">S</span>
                            <div className="thinking-indicator" aria-label="StudyMate is thinking">
                                <i /><i /><i />
                            </div>
                        </div>
                    )}
                </div>

                {messages.length === 1 && (
                    <div className="prompt-suggestions">
                        <span>Try asking</span>
                        {starterPrompts.map((prompt) => (
                            <button
                                type="button"
                                key={prompt}
                                onClick={() => sendMessage(prompt)}
                                disabled={isThinking}
                            >
                                {prompt} <span aria-hidden="true">↗</span>
                            </button>
                        ))}
                    </div>
                )}

                <div className="chat-composer">
                    <div className="mode-picker" aria-label="Choose a learning mode">
                        {learningModes.map((learningMode) => (
                            <button
                                type="button"
                                key={learningMode.id}
                                className={mode === learningMode.id ? "selected" : ""}
                                onClick={() => setMode(learningMode.id)}
                                aria-pressed={mode === learningMode.id}
                            >
                                <span aria-hidden="true">{learningMode.icon}</span>
                                {learningMode.label}
                            </button>
                        ))}
                    </div>
                    <form
                        className="chat-input-row"
                        onSubmit={(event) => {
                            event.preventDefault();
                            sendMessage();
                        }}
                    >
                        <textarea
                            ref={inputRef}
                            rows="1"
                            value={question}
                            onChange={(event) => setQuestion(event.target.value)}
                            onKeyDown={(event) => {
                                if (event.key === "Enter" && !event.shiftKey) {
                                    event.preventDefault();
                                    sendMessage();
                                }
                            }}
                            placeholder="Ask a question or describe what feels confusing..."
                            aria-label="Ask StudyMate a question"
                            disabled={isThinking}
                        />
                        <button
                            type="submit"
                            className="send-btn"
                            disabled={!question.trim() || isThinking}
                            aria-label="Send question"
                        >
                            ↑
                        </button>
                    </form>
                    <p className="prototype-note">
                        <span aria-hidden="true">ⓘ</span>
                        {token
                            ? "AI answers are powered by the StudyMate knowledge engine. Your notes are used as context."
                            : "Sign in to unlock AI-powered answers with your personal study context."}
                    </p>
                </div>
            </section>
        </section>
    );
}

export default AskAIPage;
