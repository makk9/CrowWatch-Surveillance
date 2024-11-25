import React, { useState, useEffect } from "react";

const VideoFeed = () => {
    const [feedUrl, setFeedUrl] = useState("");

    useEffect(() => {
        // Connect to the WebSocket
        const ws = new WebSocket("ws://192.168.1.100:8765");

        ws.onmessage = (message) => {
            // Decode the binary data into a base64 image string
            const blob = new Blob([message.data], { type: "image/jpeg" });
            const imageUrl = URL.createObjectURL(blob);
            setFeedUrl(imageUrl);

            // Revoke old object URLs to prevent memory leaks
            return () => URL.revokeObjectURL(imageUrl);
        };

        ws.onerror = (error) => {
            console.error("WebSocket Error:", error);
        };

        ws.onclose = () => {
            console.log("WebSocket connection closed.");
        };

        // Cleanup on component unmount
        return () => {
            ws.close();
        };
    }, []);

    return (
        <div>
            <h1>Live Video Feed</h1>
            {feedUrl ? (
                <img src={feedUrl} alt="Live Feed" style={{ maxWidth: "100%" }} />
            ) : (
                <p>Connecting to video feed...</p>
            )}
        </div>
    );
};

export default VideoFeed;
