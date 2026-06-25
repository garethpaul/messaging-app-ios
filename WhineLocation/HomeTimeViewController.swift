//
//  ViewController.swift
//  WhineLocation
//
//  Created by Gareth Jones  on 3/28/15.
//  Copyright (c) 2015 garethpaul. All rights reserved.
//

import UIKit
import Alamofire

class HomeTimeViewController: UIViewController {

    var transitionOperator = TransitionOperator()

    @IBOutlet var uiPicker: UIDatePicker!
    private var homeTimeRequest: Request?
    private var isHomeTimeViewActive = false
    private var homeTimeViewGeneration = 0

    override func viewWillAppear(animated: Bool) {
        super.viewWillAppear(animated)
        isHomeTimeViewActive = true
        homeTimeViewGeneration += 1
    }

    override func viewWillDisappear(animated: Bool) {
        super.viewWillDisappear(animated)
        isHomeTimeViewActive = false
        homeTimeViewGeneration += 1
        homeTimeRequest?.cancel()
        homeTimeRequest = nil
    }

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
        homeTimeRequest?.cancel()
        homeTimeRequest = nil

        guard isHomeTimeViewActive else {
            return
        }

        guard let userId = currentDigitsUserID() else {
            return
        }

        let requestGeneration = homeTimeViewGeneration

        let dateFormatter = NSDateFormatter()
        dateFormatter.dateFormat = "hh:mm a" //format style. Browse online to get a format that fits your needs.
        let dateString = dateFormatter.stringFromDate(uiPicker.date)

        let request = Alamofire.request(.POST, getInfo("newHometimeUrl"), parameters: ["userId": userId, "homeTime": dateString]).validate(statusCode: 200..<300)
        homeTimeRequest = request
        request.responseJSON { (req, res, json, error) in
            dispatch_async(dispatch_get_main_queue()) {
                guard self.homeTimeRequest === request else {
                    return
                }

                self.homeTimeRequest = nil
                guard self.isHomeTimeViewActive &&
                    requestGeneration == self.homeTimeViewGeneration else {
                        return
                }

                guard error == nil else {
                    return
                }

                self.performSegueWithIdentifier("presentNav", sender: self)
            }
        }
    }
    

    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject?) {
        if segue.identifier == "presentNav" {
            let toViewController = segue.destinationViewController as! UIViewController
            self.modalPresentationStyle = UIModalPresentationStyle.Custom
            toViewController.transitioningDelegate = self.transitionOperator
        }
    }
}
