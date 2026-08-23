// The single Socket.IO connection shared by every blackjack module.
// `io` is provided by the socket.io client script loaded in the template.

export const socket = io();
