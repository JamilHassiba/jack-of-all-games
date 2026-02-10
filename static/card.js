
/*
        {
            "code": "6H", 
            "image": "https://deckofcardsapi.com/static/img/6H.png", 
            "images": {
                          "svg": "https://deckofcardsapi.com/static/img/6H.svg", 
                          "png": "https://deckofcardsapi.com/static/img/6H.png"
                      }, 
            "value": "6", 
            "suit": "HEARTS"
        },
*/
export class Card {
	static #topZIndex = 0;

	static CreateCardClickbox(root, x, y) {
		const e = document.createElement('div');
		e.className = 'OBJ_cardclickbox';
		e.zIndex = 9999

		root.appendChild(e);
		
		let width = e.offsetWidth;
		let height = e.offsetHeight;
		e.style.left = x-(width/2)+'px';
		e.style.top = y-(height/2)+'px';

		return e
	}

	static #CreateDiv(root, image, face_up) {
		const e = document.createElement('img');
		e.className = 'OBJ_card'
		root.appendChild(e);
		return e		
	}

	constructor(root, card_json, face_up) {
		this.code = card_json.code;
	    this.image = card_json.image;
	    this.value = card_json.value;
	    this.suit = card_json.suit;
   		this.face_up = face_up;
    	this.div = Card.#CreateDiv(root, this.image, this.face_up);

    	// init
    	this.setImage()
	}

	setImage() {
		this.div.src = (this.face_up) ? this.image : 'https://deckofcardsapi.com/static/img/back.png';
	}

	setPosition(x, y) {
		let width = this.div.offsetWidth;
		let height = this.div.offsetHeight;
		this.div.style.left = x-(width/2)+'px';
		this.div.style.top = y-(height/2)+'px';
		this.putCardOnTop(this.div)
	}

	putCardOnTop() {
		this.div.zIndex = Card.#topZIndex;
		Card.#topZIndex++;
	}	

	destroy() {
		this.div.remove();
	}
}
