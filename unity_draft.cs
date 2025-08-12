using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Firebase;
using Firebase.Database;

public class FirebaseMapConnector : MonoBehaviour
{
    private DatabaseReference locationsRef;

    void Start()
    {
        // Initialize Firebase
        FirebaseApp.CheckAndFixDependenciesAsync().ContinueWith(task =>
        {
            var dependencyStatus = task.Result;
            if (dependencyStatus == DependencyStatus.Available)
            {
                // Firebase is ready
                InitializeDatabase();
            }
            else
            {
                Debug.LogError($"Could not resolve Firebase dependencies: {dependencyStatus}");
            }
        });
    }

    private void InitializeDatabase()
    {
        // Get the default database instance (use your database URL if multi-region)
        FirebaseDatabase database = FirebaseDatabase.DefaultInstance; // Or FirebaseDatabase.GetInstance("https://your-project.firebaseio.com/");
        
        // Reference to 'locations' path
        locationsRef = database.RootReference.Child("locations");

        // Add real-time listener for value changes
        locationsRef.ValueChanged += HandleValueChanged;
        
        Debug.Log("Firebase Realtime Database connected and listening.");
    }

    private void HandleValueChanged(object sender, ValueChangedEventArgs args)
    {
        if (args.DatabaseError != null)
        {
            Debug.LogError(args.DatabaseError.Message);
            return;
        }

        // Get the updated data snapshot
        DataSnapshot snapshot = args.Snapshot;
        
        // Process the data (e.g., dictionary of locations)
        Dictionary<string, object> locations = snapshot.Value as Dictionary<string, object>;
        
        if (locations != null)
        {
            foreach (var entry in locations)
            {
                string id = entry.Key;
                Dictionary<string, object> locData = entry.Value as Dictionary<string, object>;
                
                if (locData != null)
                {
                    float lat = System.Convert.ToSingle(locData["lat"]);
                    float lon = System.Convert.ToSingle(locData["lon"]);
                    string category = locData["category"] as string;
                    
                    // Update your Unity map here
                    // Example: Spawn or update a GameObject marker at world position (convert lat/lon to Unity coords)
                    Debug.Log($"Updated location {id}: Category={category}, Lat={lat}, Lon={lon}");
                    
                    // For user-friendly display: Cluster markers if too close (use custom logic or plugins like KDTree)
                    // Render custom icons/prefabs based on category (e.g., flame prefab for "fire")
                }
            }
        }
        else
        {
            Debug.Log("No locations data available.");
        }
    }

    void OnDestroy()
    {
        // Cleanup listener
        if (locationsRef != null)
        {
            locationsRef.ValueChanged -= HandleValueChanged;
        }
    }
}
