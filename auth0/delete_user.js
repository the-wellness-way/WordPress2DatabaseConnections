async function remove(id, callback) {
    const url = `https://ivokmm9emd.execute-api.us-east-1.amazonaws.com/tww_sso_new/delete_user?user_id=${encodeURIComponent(id)}`;
    
    try {
        const myHeaders = new Headers();
        myHeaders.append("Accept", "application/json");
        myHeaders.append("Content-Type", "application/json");

        const requestOptions = {
            method: "DELETE",
            headers: myHeaders,
            redirect: "follow"
        };

        // Await the response
        const response = await fetch(url, requestOptions);
        
        if (!response.ok) {
            // Handle error response from the API
            const errorResult = await response.json();
            return callback(new Error(`Failed to delete user: ${JSON.stringify(errorResult)}`));
        }

        // Check the result from the API
        const result = await response.json();
        if (result.success) {
            // Successfully deleted user
            return callback(null);
        } else {
            // Error in deletion process
            return callback(new Error("Failed to delete user from external database"));
        }
    } catch (error) {
        console.error("Error during user deletion:", error);
        return callback(new Error("Error deleting user data"));
    }
}
