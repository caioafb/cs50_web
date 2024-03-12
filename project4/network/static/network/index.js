function edit(id, csrfToken) {
    var div = document.getElementById(id);
    div = div.getElementsByClassName("content")[0];
    // This if prevents the edit button to be clicked multiple times
    if (div.tagName === "P") {
        var content = div.innerHTML;
        div.innerHTML = 
        `
        <form action="/new_post" method="post">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
            <div class="form-group">
                <textarea class="form-control" name="content" required>${content}</textarea>
                <input type="hidden" name="id" value=${id}>
            </div>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <input class="btn btn-primary" type="submit" value="Save">
        </form>
        `;
    }
}

function update_likes(post_id, element) {
    fetch(`/likes/${post_id}`)
        .then(response => response.json())
        .then(n_likes => {
            n_likes = n_likes["likes"];
            var likes = document.getElementById(post_id);
            likes = likes.getElementsByClassName("likes")[0];
            if (element.innerHTML === "🩶") {
                element.innerHTML = "❤️";
                likes.innerHTML = `<small>Likes: ${n_likes+1}</small>`
            }
            else {
                element.innerHTML = "🩶";
                likes.innerHTML = `<small>Likes: ${n_likes-1}</small>`
            }
        })
        // Timeout to fix like count showing incorrectly
        .then(setTimeout(() => {
            fetch(`/likes/${post_id}`, {
                method: 'PUT',
            })
          }, 50))
}