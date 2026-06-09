//
//  RequestLabs.swift
//  TheBakery
//
//  Created by Gareth Jones  on 3/18/15.
//  Copyright (c) 2015 GPJ. All rights reserved.
//

import Foundation
import Alamofire
import DigitsKit

class ShareLocation {

    // Track
    func location(lat: String, lng: String) {
        guard let userId = currentDigitsUserID() else {
            return
        }

        Alamofire.request(.POST, "https://requestlabs.appspot.com/whine/location", parameters: ["lat": lat, "lng": lng, "userId": userId])
    }
}
