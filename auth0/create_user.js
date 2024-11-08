async function create(user, callback) {
    const url = 'https://ivokmm9emd.execute-api.us-east-1.amazonaws.com/tww_sso_new/create_user';
    const user_id = user.user_id ?? user.id;
    const email = user.email;
    const password = user.password;
    
    const wpHasher = require('wordpress-hash-node');
    const hashedPassword = wpHasher.HashPassword(password);

    let data = {
        "user_id": user_id,
        "email": email,
        "password": hashedPassword
    };

    try {
        const myHeaders = new Headers();
        myHeaders.append("Accept", "application/json");
        myHeaders.append("Content-Type", "application/json");

        const raw = JSON.stringify({ data });

        const requestOptions = {
            method: "POST",
            headers: myHeaders,
            body: raw,
            redirect: "follow"
        };

        const response = await fetch(url, requestOptions);
        const result = await response.json();

        if (!result || !result.user_id) {
            return callback(null, null);
        }

        const profile = {
            user_id: result.user_id.toString(), // Ensure user_id is a string
            email: result.email,
            username: result.username || email.split('@')[0] // Optional: Use part of email if username is not provided
        };

        return callback(null, profile);
    } catch (error) {
        console.error("Error retrieving user data:", error);

        return callback(new Error("Error fetching user data"));
    }
}
