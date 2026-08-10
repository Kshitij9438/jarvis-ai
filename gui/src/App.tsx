import React, { useState } from "react";
import { sendMessageWithEvents } from "./api";
import type { ChatResponse, JarvisEvent } from "./types";
import "./styles.css";

type Message = {
    id: number;
    role: "user" | "assistant";
    content: string;
};

function resultToText(result: unknown): string {
    if (typeof result === "string") {
        return result;
    }

    if (result === null || result === undefined) {
        return "";
    }

    try {
        return JSON.stringify(result, null, 2);
    } catch {
        return String(result);
    }
}

function getEventLabel(event: JarvisEvent): string {
    const attempt = event.data.attempt;

    switch (event.type) {
        case "request.started":
            return "Request received";

        case "execution.started":
            return "Execution started";

        case "attempt.started":
            return attempt
                ? `Attempt ${String(attempt)} started`
                : "Attempt started";

        case "attempt.executed":
            return "Steps executed";

        case "evaluation.completed":
            return "Evaluation completed";

        case "plan.repaired":
            return "Plan repaired";

        case "execution.completed":
            return event.data.success
                ? "Execution completed"
                : "Execution failed";

        case "request.completed":
            return "Request completed";

        default:
            return event.type;
    }
}

function getEventState(
    event: JarvisEvent,
): "success" | "neutral" {
    if (
        event.type === "execution.completed" &&
        event.data.success === false
    ) {
        return "neutral";
    }

    return "success";
}

export default function App() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [events, setEvents] = useState<JarvisEvent[]>([]);
    const [lastResponse, setLastResponse] =
        useState<ChatResponse | null>(null);

    const [loading, setLoading] = useState(false);
    const [developerOpen, setDeveloperOpen] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function submitMessage(message?: string) {
        const value = (message ?? input).trim();

        if (!value || loading) {
            return;
        }

        setInput("");
        setError(null);
        setLoading(true);
        setEvents([]);
        setLastResponse(null);

        const userMessage: Message = {
            id: Date.now(),
            role: "user",
            content: value,
        };

        setMessages((current) => [...current, userMessage]);

        try {
            const response = await sendMessageWithEvents(value);

            setEvents(response.events);
            setLastResponse(response.response);

            const successfulResults = response.response.results
                .filter((item) => item.success)
                .map((item) => resultToText(item.result))
                .filter(Boolean);

            const assistantText =
                successfulResults.length > 0
                    ? successfulResults.join("\n\n")
                    : "Execution completed.";

            setMessages((current) => [
                ...current,
                {
                    id: Date.now() + 1,
                    role: "assistant",
                    content: assistantText,
                },
            ]);
        } catch (err) {
            const message =
                err instanceof Error
                    ? err.message
                    : "Something went wrong.";

            setError(message);

            setMessages((current) => [
                ...current,
                {
                    id: Date.now() + 1,
                    role: "assistant",
                    content: "I couldn't complete that request.",
                },
            ]);
        } finally {
            setLoading(false);
        }
    }

    function handleSubmit(
        event: React.SubmitEvent<HTMLFormElement>,
    ) {
        event.preventDefault();
        void submitMessage();
    }

    function handleComposerKeyDown(
        event: React.KeyboardEvent<HTMLTextAreaElement>,
    ) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();

            if (!loading) {
                void submitMessage();
            }
        }
    }

    function clearConversation() {
        setMessages([]);
        setEvents([]);
        setLastResponse(null);
        setError(null);
        setDeveloperOpen(false);
    }

    const hasConversation = messages.length > 0;

    return (
        <div className="jarvis-shell">
            <div className="ambient ambient-one" />
            <div className="ambient ambient-two" />

            <header className="topbar">
                <div className="brand">
                    <div className="brand-orb">
                        <span />
                    </div>

                    <div>
                        <div className="brand-name">JARVIS</div>

                        <div className="brand-status">
                            <span className="online-dot" />
                            Local runtime
                        </div>
                    </div>
                </div>

                <div className="topbar-actions">
                    {hasConversation && (
                        <button
                            className="topbar-button"
                            onClick={clearConversation}
                        >
                            Clear
                        </button>
                    )}

                    <button
                        className={`topbar-button inspector-button ${developerOpen ? "active" : ""
                            }`}
                        onClick={() =>
                            setDeveloperOpen((current) => !current)
                        }
                    >
                        <span className="inspector-icon">⌘</span>
                        Inspector
                    </button>
                </div>
            </header>

            <main className="main">
                {!hasConversation ? (
                    <section className="hero">
                        <div className="hero-orb">
                            <div className="hero-orb-inner">
                                <span />
                            </div>
                        </div>

                        <div className="hero-eyebrow">
                            LOCAL INTELLIGENCE SYSTEM
                        </div>

                        <h1>
                            What can I do
                            <br />
                            <span>for you?</span>
                        </h1>

                        <p>
                            Your local JARVIS runtime is ready.
                            <br />
                            Ask naturally. I'll figure out the rest.
                        </p>

                        <div className="suggestions">
                            <button
                                onClick={() =>
                                    void submitMessage("open github")
                                }
                            >
                                <span>↗</span>
                                Open GitHub
                            </button>

                            <button
                                onClick={() =>
                                    void submitMessage("explain")
                                }
                            >
                                <span>✦</span>
                                Explain something
                            </button>

                            <button
                                onClick={() =>
                                    void submitMessage(
                                        "what is the weather like",
                                    )
                                }
                            >
                                <span>⌕</span>
                                Search the web
                            </button>
                        </div>
                    </section>
                ) : (
                    <section className="conversation">
                        {messages.map((message) => (
                            <article
                                className={`message-row ${message.role}`}
                                key={message.id}
                            >
                                {message.role === "assistant" && (
                                    <div className="message-avatar">
                                        <span />
                                    </div>
                                )}

                                <div className="message-body">
                                    <div className="message-author">
                                        {message.role === "user"
                                            ? "You"
                                            : "JARVIS"}
                                    </div>

                                    <div className="message-text">
                                        {message.content}
                                    </div>
                                </div>
                            </article>
                        ))}

                        {loading && (
                            <article className="message-row assistant">
                                <div className="message-avatar thinking">
                                    <span />
                                </div>

                                <div className="message-body">
                                    <div className="message-author">
                                        JARVIS
                                    </div>

                                    <div className="thinking-card">
                                        <div className="thinking-orb">
                                            <span />
                                        </div>

                                        <div>
                                            <div className="thinking-title">
                                                Working on it
                                            </div>

                                            <div className="thinking-subtitle">
                                                Planning and executing your request
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </article>
                        )}
                    </section>
                )}

                {error && (
                    <div className="error-banner">
                        <span>!</span>
                        {error}
                    </div>
                )}

                {hasConversation &&
                    !loading &&
                    events.length > 0 && (
                        <button
                            className="execution-pill"
                            onClick={() => setDeveloperOpen(true)}
                        >
                            <span className="execution-check">✓</span>
                            <span>Execution completed</span>
                            <span className="execution-events">
                                {events.length} events
                            </span>
                            <span className="execution-arrow">
                                →
                            </span>
                        </button>
                    )}
            </main>

            <footer className="composer-area">
                <form
                    className={`composer ${loading ? "disabled" : ""}`}
                    onSubmit={handleSubmit}
                >
                    <textarea
                        value={input}
                        onChange={(event) =>
                            setInput(event.target.value)
                        }
                        onKeyDown={handleComposerKeyDown}
                        placeholder="Ask JARVIS anything..."
                        rows={1}
                        disabled={loading}
                    />

                    <button
                        className="send-button"
                        type="submit"
                        disabled={loading || !input.trim()}
                        aria-label="Send"
                    >
                        ↑
                    </button>
                </form>

                <div className="composer-hint">
                    <span>Enter</span>
                    <span>to send</span>
                    <span className="hint-divider">·</span>
                    <span>Shift + Enter</span>
                    <span>for new line</span>
                </div>
            </footer>

            {developerOpen && (
                <aside className="inspector">
                    <div className="inspector-header">
                        <div>
                            <div className="inspector-title">
                                Developer Inspector
                            </div>

                            <div className="inspector-subtitle">
                                Runtime diagnostics
                            </div>
                        </div>

                        <button
                            className="close-button"
                            onClick={() =>
                                setDeveloperOpen(false)
                            }
                        >
                            ×
                        </button>
                    </div>

                    <div className="inspector-content">
                        <section className="inspector-section">
                            <div className="section-label">
                                EXECUTION
                            </div>

                            <div className="timeline">
                                {events.map((event, index) => (
                                    <div
                                        className="timeline-item"
                                        key={`${event.type}-${index}`}
                                    >
                                        <div
                                            className={`timeline-dot ${getEventState(
                                                event,
                                            )}`}
                                        />

                                        <div className="timeline-line" />

                                        <div className="timeline-content">
                                            <strong>
                                                {getEventLabel(event)}
                                            </strong>

                                            <span>{event.type}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>

                        {lastResponse?.plan && (
                            <section className="inspector-section">
                                <div className="section-label">
                                    PLAN
                                </div>

                                <div className="plan-list">
                                    {lastResponse.plan.steps.map(
                                        (step, index) => (
                                            <div
                                                className="plan-step"
                                                key={`${step.action}-${index}`}
                                            >
                                                <span className="step-number">
                                                    {String(index + 1).padStart(
                                                        2,
                                                        "0",
                                                    )}
                                                </span>

                                                <div>
                                                    <strong>
                                                        {step.action}
                                                    </strong>

                                                    <span>
                                                        {
                                                            Object.keys(step.args)
                                                                .length
                                                        }{" "}
                                                        arguments
                                                    </span>
                                                </div>
                                            </div>
                                        ),
                                    )}
                                </div>
                            </section>
                        )}

                        {lastResponse && (
                            <section className="inspector-section">
                                <div className="section-label">
                                    DETAILS
                                </div>

                                <details className="raw-details">
                                    <summary>Raw response</summary>

                                    <pre>
                                        {JSON.stringify(
                                            lastResponse,
                                            null,
                                            2,
                                        )}
                                    </pre>
                                </details>
                            </section>
                        )}
                    </div>
                </aside>
            )}
        </div>
    );
}