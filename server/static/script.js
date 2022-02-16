let messages = document.getElementById("messages");

const listenForMinedBlocks = async () => {
  let numOfBlocks = document.currentScript.getAttribute('length');
  let url = new URL(`${window.location.origin}/chain/length`);
  setInterval(async () => {
    response = await fetch(url);
    result = await response.json();

    if (result.length != numOfBlocks) {
      let message = document.createElement("p");
      message.innerText = "Novos blocos minerados.";
      messages.appendChild(message);

      setTimeout(() => {
        messages.removeChild(message);
      }, 2000);
      numOfBlocks = result.length;
    }
  }, 5000);
};

listenForMinedBlocks();
