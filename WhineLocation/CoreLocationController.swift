//
//  CoreLocationController.swift
//  weatheralerts
//
//  Copyright (c) 2014 iAchieved.it LLC. All rights reserved.
//

import Foundation
import CoreLocation
import Alamofire
import Parse

class CoreLocationController : NSObject, CLLocationManagerDelegate {

    var locationManager:CLLocationManager = CLLocationManager()
    var prev: Int?
    let region = CLBeaconRegion(proximityUUID: NSUUID(UUIDString: "2F234454-CF6D-4A0F-ADF2-F4911BA9FFA6"), identifier: "couch")

    override init() {
        super.init()
        self.locationManager.delegate = self
        self.locationManager.distanceFilter  = 1000                         // Must move at least 3km
        self.locationManager.desiredAccuracy = kCLLocationAccuracyBestForNavigation // Accurate within a kilometer
        self.locationManager.activityType = CLActivityType.OtherNavigation
        self.locationManager.requestAlwaysAuthorization()
        println("setup location")
    }

    func locationManager(manager: CLLocationManager!, didChangeAuthorizationStatus status: CLAuthorizationStatus) {
        println("didChangeAuthorizationStatus")

        switch status {
        case .NotDetermined:
            println(".NotDetermined")
            break
            

        case .Denied:
            println(".Denied")
            break

        default:
            println("Unhandled authorization status")
            break

        }
    }

    // This is where all the magic happens for determing whether to render the Tweets
    func locationManager(manager: CLLocationManager!, didRangeBeacons beacons: [AnyObject]!, inRegion region: CLBeaconRegion!) {

        //println(beacons)

        let knownBeacons = beacons.filter{ $0.proximity != CLProximity.Unknown }
        if (knownBeacons.count > 0) {
            let closestBeacon = knownBeacons[0] as! CLBeacon

            // Set the proximity
            let proximity = closestBeacon.proximity.rawValue
            println("proximity")
            println(proximity)

            Alamofire.request(.GET, getInfo("beaconUrl"), parameters: ["beacon": region.identifier])

            // If the proximity does not equal the prev value set the user has become closer or further away from the beacon
            if prev != closestBeacon.proximity.rawValue {

                // If the proximity is very close - we should show some TV tweets
                if (proximity == 1){
                    println("in the house")
                }

                    // If the proximity is further away.
                else if proximity == 2 {
                    println("in the house")

                    // If the previous value was 1 aka close then we need to start again remove the tweets and wait for the
                    // user to come back in range.
                    if prev == 1 {

                    }
                }
                // set previous value
                prev = proximity
            }

        }
    }


    func locationManager(manager: CLLocationManager!, didUpdateLocations locations: [AnyObject]!) {

      let location = locations.last as! CLLocation
        location.coordinate.latitude
        let lat = "\(location.coordinate.latitude)"
        let lng = "\(location.coordinate.longitude)"
        let share = ShareLocation()
        share.location(lat, lng: lng)
    }
    
}