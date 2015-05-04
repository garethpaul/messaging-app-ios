//
//  NavigationVewController.swift
//  NavTransition
//

import Foundation
import Foundation
import UIKit
import DigitsKit

class NavigationViewController : UIViewController, UITableViewDelegate, UITableViewDataSource {

    @IBOutlet var bgImageView : UIImageView!
    @IBOutlet var tableView   : UITableView!
    @IBOutlet var dimmerView  : UIView!

    var window: UIWindow?
    let transitionManager = TransitionManager()
    var items : [NavigationModel]!

    override func viewDidLoad() {
        super.viewDidLoad()

        tableView.delegate = self
        tableView.dataSource = self
        tableView.separatorStyle = .None
        tableView.backgroundColor = UIColor.clearColor()

        bgImageView.image = UIImage(named: "whineLocationBG")
        dimmerView.backgroundColor = UIColor(white: 0.0, alpha: 0.001)

        let item1 = NavigationModel(title: "Map", icon: "map", segue: "map")
        let pulse = NavigationModel(title: "Pulse", icon: "pulseIcon", segue: "pulse")
        let item2 = NavigationModel(title: "Home Time", icon: "timeLogo", segue: "homeTime")
        let item3 = NavigationModel(title: "Logout", icon: "logout", segue: "logout")
        
        items = [item1, pulse, item2, item3]
    }

    func tableView(tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return items.count
    }

    func tableView(tableView: UITableView, cellForRowAtIndexPath indexPath: NSIndexPath) -> UITableViewCell {

        let cell = tableView.dequeueReusableCellWithIdentifier("NavigationCell") as! NavigationCell

        let item = items[indexPath.row]

        cell.titleLabel.text = item.title
        cell.countLabel.text = item.count
        cell.iconImageView.image = UIImage(named: item.icon)!.imageWithRenderingMode(.AlwaysTemplate)
        cell.iconImageView.tintColor = UIColor.whiteColor()
        cell.backgroundColor = UIColor.clearColor()

        return cell
    }

    func tableView(tableView: UITableView, didSelectRowAtIndexPath indexPath: NSIndexPath) {


        let item = items[indexPath.row]
        let segue = item.segue

        if segue == "logout" {
            Digits.sharedInstance().logOut()
            performSegueWithIdentifier(segue, sender: self)

        }

        performSegueWithIdentifier(segue, sender: self)

    }

    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject?) {

        // this gets a reference to the screen that we're about to transition to
        let toViewController = segue.destinationViewController as! UIViewController

        // instead of using the default transition animation, we'll ask
        // the segue to use our custom TransitionManager object to manage the transition animation
        toViewController.transitioningDelegate = self.transitionManager

    }


    override func preferredStatusBarStyle() -> UIStatusBarStyle {
        return .LightContent
    }
}

class NavigationModel {

    var title : String!
    var segue : String!
    var icon : String!
    var count : String?

    init(title: String, icon : String, segue: String!){
        self.title = title
        self.icon = icon
        self.segue = segue
    }
    
    init(title: String, icon : String, segue: String!, count: String){
        
        self.title = title
        self.icon = icon
        self.count = count
        self.segue = segue
    }
}
