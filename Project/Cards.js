
function cardClick(event) {
    console.log("card clicked");
}

function setCards(response) {
    //console.log(response);
    for (var i = 0; i < 2; i++) {
        var div = document.createElement("div");
        div.className += "wrapper";
        var anchor = document.createElement("a");
        //anchor.href = "AdView.html?adid=" + response[i].adid + "&" + "category=" + response[i].category;

        anchor.className = "anchor-text";
        var itembox = document.createElement("DIV");
        itembox.className += "card_item";

        var itemimage = document.createElement("DIV");
        itemimage.className += "card_img";
        var itemtext = document.createElement("DIV");
        itemtext.className += "card_text";

        /*var fav = document.createElement("span");
        if (response[i].isfavourite)
            fav.className += "span-favourite-on";
        else
            fav.className += "span-favourite-off";

        fav.id = response[i].adid;
        fav.onclick = function() {
            addToFavourite(this)
        };

        div.appendChild(fav);
*/
        var img = document.createElement("img");
        img.setAttribute("src", response[i].path);
        itemimage.appendChild(img);

        var price = document.createElement("span");
        price.textContent = response[i].name;
        price.className = "price-text";
        itemtext.appendChild(price);

        /*var title = document.createElement("span");
        title.textContent = response[i].name;
        title.className = "title-text";
        itemtext.appendChild(title);

        var desc = document.createElement("span");
        desc.textContent = response[i].description;
        desc.className += "title-text";
        itemtext.append(desc);

        var date = document.createElement("span");
        date.textContent = response[i].date;
        date.className += "title-text date";
        itemtext.append(date);*/

        itembox.appendChild(itemimage);
        itembox.appendChild(itemtext);
        anchor.appendChild(itembox);
        div.appendChild(anchor);
        document.getElementById("card_items").appendChild(div);
    }

}