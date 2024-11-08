async function verify(email, callback) {
    const url = 'https://ivokmm9emd.execute-api.us-east-1.amazonaws.com/tww_sso_new/verify';
  
    try {
      const myHeaders = new Headers();
      myHeaders.append("Accept", "application/json");
      myHeaders.append("Content-Type", "application/json");
  
      const raw = JSON.stringify({
        "email": email,
        "is_active": 1  // Assuming 1 means verified/active
      });
  
      const requestOptions = {
        method: "POST",
        headers: myHeaders,
        body: raw,
        redirect: "follow"
      };
  
      const response = await fetch(url, requestOptions);
      const result = await response.json();
  
      if (!result || result.error) {
        // Return an error if verification fails
        return callback(new Error("Failed to verify email: " + JSON.stringify(result)));
      }
  
      // Verification succeeded
      return callback(null, true);
    } catch (error) {
      console.error("Error verifying email:", error);
      return callback(new Error("Error verifying email"));
    }
  }
  