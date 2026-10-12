import { useState } from "react";

function NoteForm({ onAddNote, onCancel }) {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [topics, setTopics] = useState("");
    const [error, setError] = useState("");
    const [saving, setSaving] = useState(false);

    async function handleSubmit(event) {
        event.preventDefault();
        setError("");

        const topicCount = Number(topics);
        if (!title.trim() || !description.trim()) {
            setError("Please add a title and description before saving.");
            return;
        }

        if (!Number.isInteger(topicCount) || topicCount <= 0) {
            setError("Enter a whole number of topics greater than zero.");
            return;
        }

        setSaving(true);
        try {
            await onAddNote({
                title: title.trim(),
                description: description.trim(),
                topics: topicCount
            });
            setTitle("");
            setDescription("");
            setTopics("");
            onCancel();
        } catch (saveError) {
            setError(saveError.message || "Could not save this note.");
        } finally {
            setSaving(false);
        }
    }

    return (
        <form
            className="note-form"
            onSubmit={handleSubmit}
            noValidate
        >
            <div className="form-heading">
                <div>
                    <p className="form-kicker">NEW NOTE</p>
                    <h3>Create a New Note</h3>
                </div>
                <button
                    className="form-close"
                    type="button"
                    onClick={onCancel}
                    aria-label="Close form"
                >
                    ×
                </button>
            </div>

            <label htmlFor="note-title">Note title</label>
            <input
                id="note-title"
                type="text"
                placeholder="e.g. Introduction to Biology"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
            />

            <label htmlFor="note-description">Description</label>
            <textarea
                id="note-description"
                placeholder="What are you learning in this note?"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
            />

            <label htmlFor="note-topics">Number of topics</label>
            <input
                id="note-topics"
                type="number"
                min="1"
                step="1"
                placeholder="e.g. 5"
                value={topics}
                onChange={(event) => setTopics(event.target.value)}
            />

            {error && <p className="form-error" role="alert">{error}</p>}

            <div className="form-actions">
                <button type="submit" className="save-btn" disabled={saving}>
                    {saving ? "Saving..." : "Save Note"}
                </button>
                <button type="button" className="cancel-btn" disabled={saving} onClick={onCancel}>
                    Cancel
                </button>
            </div>
        </form>
    );
}

export default NoteForm;