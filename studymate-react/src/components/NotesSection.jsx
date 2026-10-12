import { useEffect, useState } from "react";
import { apiRequest, mapNote } from "../lib/api";
import AuthPanel from "./AuthPanel";
import NoteCard from "./NoteCard";
import NoteForm from "./NoteForm";

function NotesSection({ showForm, onCloseForm, token, onAuthenticated, onSignOut }) {
    const [notesState, setNotesState] = useState({ token: null, notes: [] });
    const notes = notesState.token === token ? notesState.notes : [];
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(false);
    const [errorState, setErrorState] = useState({ token: null, message: "" });
    const error = errorState.token === token ? errorState.message : "";
    const [deletingId, setDeletingId] = useState(null);

    useEffect(() => {
        if (!token) {
            return undefined;
        }

        const controller = new AbortController();
        const search = searchTerm.trim();
        const timer = window.setTimeout(async () => {
            setLoading(true);
            setErrorState({ token, message: "" });
            try {
                const path = search
                    ? `/notes/search?q=${encodeURIComponent(search)}`
                    : "/notes";
                const result = await apiRequest(path, {
                    token,
                    signal: controller.signal
                });
                setNotesState({ token, notes: result.map(mapNote) });
            } catch (requestError) {
                if (requestError.name !== "AbortError") {
                    setErrorState({
                        token,
                        message: requestError.message || "Could not load notes."
                    });
                }
            } finally {
                if (!controller.signal.aborted) {
                    setLoading(false);
                }
            }
        }, search ? 250 : 0);

        return () => {
            window.clearTimeout(timer);
            controller.abort();
        };
    }, [token, searchTerm]);

    async function addNote(newNote) {
        const saved = await apiRequest("/notes", {
            token,
            method: "POST",
            body: JSON.stringify({
                title: newNote.title,
                description: newNote.description,
                topics_count: newNote.topics
            })
        });
        const mapped = mapNote(saved);
        const search = searchTerm.trim().toLocaleLowerCase();
        if (!search || mapped.title.toLocaleLowerCase().includes(search) ||
            mapped.description.toLocaleLowerCase().includes(search)) {
            setNotesState((current) => ({
                token,
                notes: [mapped, ...(current.token === token ? current.notes : [])]
            }));
        }
        setErrorState({ token, message: "" });
    }

    async function deleteNote(id) {
        setDeletingId(id);
        setErrorState({ token, message: "" });
        try {
            await apiRequest(`/notes/${encodeURIComponent(id)}`, {
                token,
                method: "DELETE"
            });
            setNotesState((current) => ({
                token,
                notes: current.token === token
                    ? current.notes.filter((note) => note.id !== id)
                    : []
            }));
        } catch (requestError) {
            setErrorState({
                token,
                message: requestError.message || "Could not delete this note."
            });
        } finally {
            setDeletingId(null);
        }
    }

    return (
        <section className="notes-section" id="notes">
            <div className="section-heading">
                <div>
                    <p className="section-label">YOUR KNOWLEDGE</p>
                    <h2>My Study Notes</h2>
                    <p className="section-description">
                        Everything you are learning, gathered in one place.
                    </p>
                </div>
                {token && (
                    <div className="note-count">
                        <strong>{notes.length}</strong>
                        <span>{notes.length === 1 ? "note" : "notes"} saved</span>
                    </div>
                )}
            </div>

            {!token ? (
                <AuthPanel onAuthenticated={onAuthenticated} />
            ) : (
                <>
                    <div className="notes-toolbar">
                        <label className="search-box">
                            <span aria-hidden="true">⌕</span>
                            <input
                                type="search"
                                placeholder="Search your notes..."
                                value={searchTerm}
                                onChange={(event) => setSearchTerm(event.target.value)}
                                aria-label="Search notes by title or description"
                            />
                        </label>
                        <button className="cancel-btn signout-btn" type="button" onClick={onSignOut}>
                            Sign out
                        </button>
                    </div>

                    {error && <p className="form-error api-error" role="alert">{error}</p>}
                    {showForm && <NoteForm onAddNote={addNote} onCancel={onCloseForm} />}

                    {loading ? (
                        <div className="empty-state" role="status"><p>Loading your notes...</p></div>
                    ) : notes.length > 0 ? (
                        <div className="notes-container">
                            {notes.map((note) => (
                                <NoteCard
                                    key={note.id}
                                    id={note.id}
                                    title={note.title}
                                    description={note.description}
                                    topics={note.topics}
                                    isDeleting={deletingId === note.id}
                                    onDelete={deleteNote}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="empty-state">
                            <span className="empty-icon" aria-hidden="true">✎</span>
                            <h3>{searchTerm.trim() ? "No notes found" : "Your study space is ready"}</h3>
                            <p>
                                {searchTerm.trim()
                                    ? "Try another title or description to find what you are looking for."
                                    : "No notes yet. Start building your knowledge by creating your first note."}
                            </p>
                        </div>
                    )}
                </>
            )}
        </section>
    );
}

export default NotesSection;
