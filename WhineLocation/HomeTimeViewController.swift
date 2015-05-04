//
//  ViewController.swift
//  WhineLocation
//
//  Created by Gareth Jones  on 3/28/15.
//  Copyright (c) 2015 garethpaul. All rights reserved.
//

import UIKit
import DigitsKit
import Alamofire

class HomeTimeViewController: UIViewController {

    var transitionOperator = TransitionOperator()

    @IBOutlet var uiPicker: UIDatePicker!



    override func viewDidLoad() {
        super.viewDidLoad()
        uiPicker.backgroundColor = UIColor.whiteColor()
        uiPicker.datePickerMode = UIDatePickerMode.Time

    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    func handler(sender: UIDatePicker) {
        var timeFormatter = NSDateFormatter()
        timeFormatter.timeStyle = NSDateFormatterStyle.ShortStyle
        var strDate = timeFormatter.stringFromDate(uiPicker.date)
    }

    @IBAction func btnClick(sender: AnyObject) {
        performSegueWithIdentifier("presentNav", sender: self)
    }
    
    @IBAction func sendTime(sender: AnyObject) {
        let userId = Digits.sharedInstance().session().userID
        var dateFormatter = NSDateFormatter()
        dateFormatter.dateFormat = "hh:mm a" //format style. Browse online to get a format that fits your needs.
        var dateString = dateFormatter.stringFromDate(uiPicker.date)
        
        Alamofire.request(.GET, getInfo("newHometimeUrl"), parameters: ["userId": userId, "homeTime": dateString])
        performSegueWithIdentifier("presentNav", sender: self)
        
    }
    

    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject?) {
        if segue.identifier == "presentNav" {
            let toViewController = segue.destinationViewController as! UIViewController
            self.modalPresentationStyle = UIModalPresentationStyle.Custom
            toViewController.transitioningDelegate = self.transitionOperator
        }
    }
}

