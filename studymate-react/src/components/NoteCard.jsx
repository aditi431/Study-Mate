function NoteCard({
    id,
    title,
    description,
    topics,
    onDelete,
    isDeleting
}) {

    return (
        <article className="note-card">
            <div className="note-card-top">
                <span className="note-icon" aria-hidden="true">✦</span>
                <button
                    className="delete-btn"
                    type="button"
                    disabled={isDeleting}
                    onClick={() => onDelete(id)}
                    aria-label={`Delete ${title}`}
                >
                    {isDeleting ? "Deleting..." : "Delete"}
                </button>
            </div>
            <h3>{title}</h3>
            <p>{description}</p>
            <div className="note-card-footer">
                <span className="topic-count">
                    <span aria-hidden="true">▤</span>
                    {topics} {topics === 1 ? "topic" : "topics"}
                </span>
                <span className="card-arrow" aria-hidden="true">↗</span>
            </div>
        </article>
    );
}

export default NoteCard;