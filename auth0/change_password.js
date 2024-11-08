async function changePassword(email, newPassword, callback) {
    const url = 'https://ivokmm9emd.execute-api.us-east-1.amazonaws.com/tww_sso_new/change_password';
    const test_password = 'newpass';
    const wpHasher = require('wordpress-hash-node');
    const hashedPassword = wpHasher.HashPassword(test_password);
    
    try {
          const myHeaders = new Headers();
          myHeaders.append("Accept", "application/json");
          myHeaders.append("Content-Type", "application/json");
  
          const raw = JSON.stringify({ 
              "email": email, 
              "password": "newPassword", 
              "newPassword": hashedPassword 
          });
  
          const requestOptions = {
              method: "POST",
              headers: myHeaders,
              body: raw,
              redirect: "follow"
          };
  
          const response = await fetch(url, requestOptions);
          const result = await response.json();
        
          if (!result) {
              return callback(new Error(JSON.stringify(result)));
          }

          return callback(null, result);
      } catch (error) {
          console.error("Error during user authentication:", error);
          return callback(new Error("Error fetching user data"));
      }
  }
  