//
//  Dictionary.swift
//  WhineLocation
//
//  Created by Gareth on 5/19/15.
//  Copyright (c) 2015 garethpaul. All rights reserved.
//

import Foundation
//

func getInfo(str: String) -> String {
    if let path = NSBundle.mainBundle().pathForResource("Info", ofType: "plist") {
        if let dict = NSDictionary(contentsOfFile: path) {
            if let value = dict.valueForKey(str) as? String {
                return value
            }
        }
    }

    return ""
}
