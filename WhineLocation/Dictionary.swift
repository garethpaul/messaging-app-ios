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
    let path = NSBundle.mainBundle().pathForResource("Info", ofType: "plist")
    let dict = NSDictionary(contentsOfFile: path!)
    let value = dict!.valueForKey(str) as? String
    return value!
}
