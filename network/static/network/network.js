document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.edit').forEach(function(element) {
    element.addEventListener('click', () => edit())
  });
  document.querySelectorAll('.like').forEach(function(element) {
    element.addEventListener('click', event => react(event))
  });
    document.querySelector('#post-form').addEventListener( 'submit', submit_form);
  });

  function submit_form(event){
    const body = document.querySelector('#body').value;
  
    fetch('/addpost', {
      method: 'POST',
      body: JSON.stringify({
          body: body
      })
    })
    .then(response => response.json())
    .then(result => {

    if(result.message == null)
    {
        document.querySelector('#body').value = "";
    }
    else
    {
      console.log(result.error);
        event.preventDefault();
    }
    });
    
  }
  
    function edit(){
      const post_container = event.target.parentElement;
      var post_id = post_container.dataset.post;
      var old_post = post_container.innerHTML;
      fetch(`/posts/${post_id}`)
      .then(response => response.json())
      .then(post => {
        post_container.className="p-2 d-flex flex-column";
      post_container.innerHTML = `
      <b>${post.user}</b>
      <textarea rows="4" id="new_body">${post.body}</textarea>
      <hr>
      <button id="save" class="right btn btn-dark">Save</button>`;
      post_container.addEventListener('click', function() {
        const element = event.target;
          if (element.id === 'save'){

            var new_body = post_container.querySelector('#new_body').value;

            fetch(`/edit/${post.id}`, {
              method: 'PUT',
              body: JSON.stringify({
                body: new_body
              })
            })
            .then(() => {
              post_container.className="p-2";
            post_container.innerHTML = old_post;
            post_container.querySelector('#body').innerHTML = new_body;
            post_container.querySelector('.edit').addEventListener('click', () => edit());
            post_container.querySelector('.like').addEventListener('click', event => react(event));
            })
          }
        });
      });
    }
    function react(event){
      const post_container = event.target.parentElement;

      var post_id = post_container.dataset.post;
      var like = event.target.dataset.like;
      
      if(like === 'like'){
        fetch(`/like/${post_id}`, {
          method: 'PUT'
        })
        .then(res => res.json())
        .then( result => {
        post_container.querySelector('#likes').innerHTML = parseInt(post_container.querySelector('#likes').innerHTML) + 1;
        post_container.querySelector('.like').innerHTML = "Unlike";
        post_container.querySelector('.like').dataset.like =  result.like_id;
        })
        
      }
      else{
        fetch(`/like/${post_id}`, {
          method: 'DELETE',
          body: JSON.stringify({
            like: like
          })
        })
        .then( () =>  {
        post_container.querySelector('#likes').innerHTML = parseInt(post_container.querySelector('#likes').innerHTML) - 1;
        post_container.querySelector('.like').innerHTML = "Like";
        post_container.querySelector('.like').dataset.like = "like";
      })
      }
    }