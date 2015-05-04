//
//  PulseViewController.swift
//  WhineLocation
//
//  Created by Gareth Jones  on 3/30/15.
//  Copyright (c) 2015 garethpaul. All rights reserved.
//

import Foundation
import UIKit
import Alamofire
import DigitsKit
import QuartzCore
import Parse

class PulseViewController: UIViewController, UITableViewDelegate, UITableViewDataSource, UITextFieldDelegate
{

    @IBOutlet var textField: UITextField!
    @IBOutlet var contentView: UIView!
    @IBOutlet var sendBtn: UIButton!
    @IBOutlet var bottomToolbar: UIToolbar!
    @IBOutlet var tableView: UITableView!

    var refreshControl:UIRefreshControl!

    func configureTableView() {
        //self.tableView.registerClass(UITableViewCell.self, forCellReuseIdentifier: "cell")
        self.tableView.rowHeight = UITableViewAutomaticDimension
        self.tableView.estimatedRowHeight = 160.0
    }

    var transitionOperator = TransitionOperator()

    var dataType: [String] = []
    var dataInfo: [String] = []
    var dataDate: [String] = []
    var dataId: [String] = []
    var dataRead: [String] = []
    var sendAvailable = true

    func getData() {

        // clear data
        dataDate.removeAll(keepCapacity: false)
        dataInfo.removeAll(keepCapacity: false)
        dataType.removeAll(keepCapacity: false)
        
        Alamofire.request(.POST, getInfo("pulseListUrl"), parameters: ["userId": Digits.sharedInstance().session().userID]).responseJSON { (req, res, json, error) in
            if (error != nil) {
                println(error)
            } else {
                var json = JSON(json!)

                for (index: String, subJson: JSON) in json {
                    //Do something you want

                    if let _dataType = subJson["dataType"].string {
                        self.dataType.append(_dataType)
                    }

                    if let _dataInfo = subJson["dataInfo"].string {
                        self.dataInfo.append(_dataInfo)
                    }

                    if let _dataDate = subJson["date"].string {
                        self.dataDate.append(_dataDate)
                    }

                    if let _dataId = subJson["rndId"].string {
                        self.dataId.append(_dataId)
                    }

                    if let _dataRead = subJson["isRead"].string {
                        self.dataRead.append(_dataRead)
                        println(_dataRead)
                    }
                }

                dispatch_async(dispatch_get_main_queue(), { () -> Void in
                    self.tableView.reloadData()
                    
                    compareRead(self.dataId)
                })
                self.refreshControl.endRefreshing()

            }
        }
        
        
    }


    // move bar up
    var kbHeight: CGFloat!

    override func viewDidLoad() {
        super.viewDidLoad()
        textField.delegate = self
        getData()


        // pull to refresh
        self.refreshControl = UIRefreshControl()
        self.refreshControl.attributedTitle = NSAttributedString(string: "Pull to refresh")
        self.refreshControl.addTarget(self, action: "refresh:", forControlEvents: UIControlEvents.ValueChanged)
        self.tableView.addSubview(refreshControl)

        configureTableView()
    }

    override func viewWillAppear(animated:Bool) {
        super.viewWillAppear(animated)

        NSNotificationCenter.defaultCenter().addObserver(self, selector: Selector("keyboardWillShow:"), name: UIKeyboardWillShowNotification, object: nil)
        NSNotificationCenter.defaultCenter().addObserver(self, selector: Selector("keyboardWillHide:"), name: UIKeyboardWillHideNotification, object: nil)

        NSTimer.scheduledTimerWithTimeInterval(
            30.0,
            target: self,
            selector: Selector("getData"),
            userInfo: nil,
            repeats: true)

    }


    override func viewWillDisappear(animated: Bool) {
        super.viewWillDisappear(animated)

        NSNotificationCenter.defaultCenter().removeObserver(self)
    }

    func keyboardWillShow(notification: NSNotification) {
        if let userInfo = notification.userInfo {
            if let keyboardSize =  (userInfo[UIKeyboardFrameBeginUserInfoKey] as? NSValue)?.CGRectValue() {
                kbHeight = keyboardSize.height
                self.animateTextField(true)
            }
        }
    }

    func keyboardWillHide(notification: NSNotification) {
        self.animateTextField(false)
    }

    func animateTextField(up: Bool) {
        var movement = (up ? -kbHeight : kbHeight)

        UIView.animateWithDuration(0.3, animations: {
            self.bottomToolbar.frame = CGRectOffset(self.bottomToolbar.frame, 0, movement)
        })
    }



    @IBAction func sendMsg(sender: AnyObject) {

        if sendAvailable == true {

            // send Available is False
            sendAvailable == false

            // Display button to red when sending
            self.sendBtn.setTitleColor(UIColor.redColor(), forState: UIControlState.Normal)

            // Send HTTP Request
            Alamofire.request(.POST, getInfo("pulseListSendUrl"), parameters: ["userId": Digits.sharedInstance().session().userID, "phoneNumber": Digits.sharedInstance().session().phoneNumber, "msg": self.textField.text])

            // Set Text Field Empty
            self.textField.text = ""

            // After 2 seconds perform request to get data
            let delayTime = dispatch_time(DISPATCH_TIME_NOW,
                Int64(1 * Double(NSEC_PER_SEC)))
            dispatch_after(delayTime, dispatch_get_main_queue()) {

                // Get the data
                self.getData()

                // Set availability to send to true
                self.sendAvailable == true

                // Display button back to white
                self.sendBtn.setTitleColor(UIColor.whiteColor(), forState: UIControlState.Normal)


            }

        }


    }


    func refresh(sender:AnyObject)
    {
        //self.view.setNeedsDisplay()
        
        getData()

    }

    // Deal with text for sending messages
    func textFieldShouldReturn(textField: UITextField) -> Bool {
        textField.resignFirstResponder()

        return true
    }

    
    func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return self.dataDate.count

    }

    func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {

        // handle messages
        if dataType[indexPath.row] == "sent_msg" {
            var  cell:DirectMessageCell! = tableView.dequeueReusableCellWithIdentifier("cell") as? DirectMessageCell

            if (cell == nil) {
                let nib:Array = NSBundle.mainBundle().loadNibNamed("DirectMessageCell", owner: self, options: nil)
                cell = nib[0] as? DirectMessageCell
            }

            cell.messageLabel.text = dataInfo[indexPath.row]
            cell.timeLabel.text = dataDate[indexPath.row]
            cell.messageLabel.sizeToFit()

            if dataRead[indexPath.row] == "true" {
                cell.msgRead.hidden = false
            }

            let txtLength = count(dataInfo[indexPath.row])

            var contentViewWidth = Float(self.contentView.frame.width)
            var maxWidth = CGFloat(((2.5*Float(txtLength))*(contentViewWidth/100))-contentViewWidth)

            cell.wrapMessage.layer.cornerRadius = 20;
            cell.wrapMessage.layer.masksToBounds = true

            let leftConstraint = NSLayoutConstraint(item: cell.contentView,
                attribute: .Left,
                relatedBy: .Equal,
                toItem: cell.wrapMessage,
                attribute: .Left,
                multiplier: 1.0,
                constant: maxWidth + 30);

            cell.contentView.addConstraint(leftConstraint)

            return cell

        } else if dataType[indexPath.row] == "message" {
            var  cell:ReceievedMessageCell! = tableView.dequeueReusableCellWithIdentifier("cell") as? ReceievedMessageCell

            if (cell == nil) {
                let nib:Array = NSBundle.mainBundle().loadNibNamed("ReceivedMessage", owner: self, options: nil)
                cell = nib[0] as? ReceievedMessageCell
            }

            cell.messageLabel.text = dataInfo[indexPath.row]
            cell.timeLabel.text = dataDate[indexPath.row]
            cell.messageLabel.sizeToFit()

            let txtLength = count(dataInfo[indexPath.row])
            var contentViewWidth = CGFloat(self.contentView.frame.width)


            // 426-(15*40)
            var maxWidth = (contentViewWidth) - (15) * CGFloat(txtLength)

            cell.wrapMessage.layer.cornerRadius = 20;
            cell.wrapMessage.layer.masksToBounds = true

            let leftConstraint = NSLayoutConstraint(item: cell.contentView,
                attribute: .Right,
                relatedBy: .Equal,
                toItem: cell.wrapMessage,
                attribute: .Right,
                multiplier: 1.0,
                constant: maxWidth)

            cell.contentView.addConstraint(leftConstraint)
            
            
            return cell


        }


            var  cell:PulseTableCell! = tableView.dequeueReusableCellWithIdentifier("cell") as? PulseTableCell

            if (cell == nil) {
                let nib:Array = NSBundle.mainBundle().loadNibNamed("PulseTableCell", owner: self, options: nil)
                cell = nib[0] as? PulseTableCell
            }

            cell.messageLabel.text = dataInfo[indexPath.row]
            cell.timeLabel.text = dataDate[indexPath.row]
            cell.imgView.image = UIImage(named: dataType[indexPath.row] + "Icon")

            
            return cell

    }

    func tableView(tableView: UITableView, heightForRowAtIndexPath indexPath: NSIndexPath) -> CGFloat {
        return CGFloat(109)
    }

    func tableView(tableView: UITableView, didSelectRowAtIndexPath indexPath: NSIndexPath) {
        
    }

    // Handle Menu
    @IBAction func btnClick(sender: AnyObject) {
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