// ==========================================
// STUDYMATE - JAVASCRIPT
// ==========================================


// ==========================================
// 1. APPLICATION DATA
// ==========================================

let appName = "StudyMate";

let studentName = "Aditi";

let isLearning = true;


// Our notes data

let notes = [

    {
        title: "Machine Learning",
        description: "Introduction to supervised and unsupervised learning.",
        topics: 5
    },

    {
        title: "Deep Learning",
        description: "Neural networks and deep learning fundamentals.",
        topics: 8
    },

    {
        title: "Data Structures",
        description: "Arrays, strings, stacks and queues.",
        topics: 10
    }

];


// ==========================================
// 2. FIND HTML ELEMENTS
// ==========================================

// Add Note button

let addNoteButton = document.querySelector("#addNoteBtn");

// Note form

let noteForm = document.querySelector("#noteForm");

// Save Note button

let saveNoteButton = document.querySelector("#saveNoteBtn");

// Notes container

let notesContainer = document.querySelector("#notesContainer");

// Input fields

let noteTitleInput = document.querySelector("#noteTitle");

let noteDescriptionInput =
    document.querySelector("#noteDescription");

let noteTopicsInput =
    document.querySelector("#noteTopics");


// ==========================================
// 3. DISPLAY EXISTING NOTES
// ==========================================

function displayNotes() {

    // Clear the container first

    notesContainer.innerHTML = "";


    // Go through every note

    notes.forEach(function(note, index) {

        // Create HTML for the note

        let noteHTML = `

            <div class="note-card">

                <h3>${note.title}</h3>

                <p>
                    ${note.description}
                </p>

                <span>
                    ${note.topics} topics
                </span>

                <br><br>

                <button
                    class="delete-btn"
                    data-index="${index}"
                >
                    Delete
                </button>

            </div>

        `;


        // Add the note card to the page

        notesContainer.innerHTML += noteHTML;

    });

}


// ==========================================
// 4. SHOW NOTE FORM
// ==========================================

addNoteButton.addEventListener("click", function() {

    noteForm.style.display = "flex";

});


// ==========================================
// 5. SAVE NEW NOTE
// ==========================================

saveNoteButton.addEventListener("click", function() {


    // Get values from input fields

    let title = noteTitleInput.value.trim();

    let description =
        noteDescriptionInput.value.trim();

    let topics =
        noteTopicsInput.value.trim();


    // ======================================
    // VALIDATION
    // ======================================

    if (title === "") {

        alert("Please enter a note title.");

        return;

    }


    if (description === "") {

        alert("Please enter a note description.");

        return;

    }


    if (topics === "") {

        alert("Please enter the number of topics.");

        return;

    }


    // ======================================
    // CREATE NEW NOTE OBJECT
    // ======================================

    let newNote = {

        title: title,

        description: description,

        topics: topics

    };


    // ======================================
    // ADD NOTE TO ARRAY
    // ======================================

    notes.push(newNote);


    // ======================================
    // UPDATE THE UI
    // ======================================

    displayNotes();


    // ======================================
    // CLEAR INPUT FIELDS
    // ======================================

    noteTitleInput.value = "";

    noteDescriptionInput.value = "";

    noteTopicsInput.value = "";


    // ======================================
    // HIDE FORM
    // ======================================

    noteForm.style.display = "none";


    console.log("New note added:", newNote);

});


// ==========================================
// 6. DELETE NOTE
// ==========================================

notesContainer.addEventListener("click", function(event) {


    // Check if the clicked element is a delete button

    if (event.target.classList.contains("delete-btn")) {


        // Get the index of the note

        let index = event.target.dataset.index;


        // Remove note from array

        notes.splice(index, 1);


        // Display updated notes

        displayNotes();


        console.log("Note deleted.");

    }

});


// ==========================================
// 7. INITIAL DISPLAY
// ==========================================

displayNotes();