let topZIndex = 1

export function PutDivOnTop(div) {
	div.style.zIndex = topZIndex;
	topZIndex += 1;
}

export function SetDivPosition(div, x, y) {
	let width = div.offsetWidth;
	let height = div.offsetHeight;
	div.style.left = x-(width/2)+'px';
	div.style.top = y-(height/2)+'px';
	PutDivOnTop(div)
}

export function DragDiv(div) {
	let x = 0;
	let y = 0;
	let nx = 0;
	let ny = 0;

	div.onmousedown = DragBegan;

	function DragBegan(e) {
		e = e || window.event;
		e.preventDefault();

		// get the mouse cursor position at startup
		x = e.clientX;
		y = e.clientY;

		PutDivOnTop(div)

		document.onmouseup = DragEnd;
		document.onmousemove = Drag;
	}

	function Drag(e) {
		e = e || window.event;
		e.preventDefault();

		// calculate the new cursor position
		nx = x - e.clientX;
		ny = y - e.clientY;

		div.style.top = (div.offsetTop - ny) + 'px';
		div.style.left = (div.offsetLeft - nx) + 'px';

		x = e.clientX;
		y = e.clientY;
	}

	function DragEnd() {
		document.onmouseup = null;
		document.onmousemove = null;
	}
}