document.getElementById("signup-form").addEventListener("submit", function (e) {
    e.preventDefault();
  
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
  
    console.log("Parent Account Created:");
    console.log("Username:", username);
    console.log("Email:", email);
    console.log("Password:", password);
  
    alert("Account created successfully!");
    this.reset();
  });
  