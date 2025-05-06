//function addComment(productId) {
//    fetch(`/api/products/${productId}/comments`, {
//        method: 'post',
//        body: JSON.stringify({
//            'content': document.getElementById('content').value
//        }),
//        headers: {
//            'Content-Type': 'application/json'
//        }
//    }).then(res => res.json()).then(c => {
//
//        let m = document.getElementById("myComments");
//        m.innerHTML = `
//           <li class="list-group-item">
//                <div class="row">
//                    <div class="col-md-1 md-4">
//                        <img class="img-fluid rounded-circle"
//                             src="${c.user.avatar}"/>
//                    </div>
//                    <div class="col-md-11 md-8">
//                        <p>${c.content}</p>
//                        <p class="created-date">${moment(c.created_date).locale('vi').fromNow()}</p>
//                    </div>
//                </div>
//            </li>
//        ` + m.innerHTML;
//    })
//}
function addComment(productId) {
    fetch(`/api/products/${productId}/comments`, {
        method: 'POST',
        body: JSON.stringify({
            'content': document.getElementById('content').value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(data => {
                throw new Error(data.error);
            });
        }
        return res.json();
    })
    .then(c => {
        let m = document.getElementById("myComments");
        m.innerHTML = `
           <li class="list-group-item">
                <div class="row">
                    <div class="col-md-1 md-4">
                        <img class="img-fluid rounded-circle"
                             src="${c.user.avatar}"/>
                    </div>
                    <div class="col-md-11 md-8">
                        <p>${c.content}</p>
                        <p class="created-date">${moment(c.created_date).locale('vi').fromNow()}</p>
                    </div>
                </div>
            </li>
        ` + m.innerHTML;
                // Tải lại trang khi bình luận thành công
        window.location.reload();
    })
    .catch(error => {
        alert(error.message); // Hiển thị thông báo lỗi nếu người dùng chưa mua sản phẩm
    });
}
