//
//  ViewController.swift
//  WhineLocation
//
//  Created by Gareth Jones  on 3/28/15.
//  Copyright (c) 2015 garethpaul. All rights reserved.
//

import UIKit
import MapKit

class ViewController: UIViewController, MKMapViewDelegate, CLLocationManagerDelegate {

    @IBOutlet var map: MKMapView!

    var transitionOperator = TransitionOperator()
    var logoView: UIImageView!

    override func viewDidLoad() {
        super.viewDidLoad()

        // Add the logo view to the top (not in the navigation bar title to have it bigger).
        logoView = UIImageView(frame: CGRectMake(0, 0, 40, 40))
        logoView.image = UIImage(named: "miniLogo")
        logoView.frame.origin.x = (self.view.frame.size.width - logoView.frame.width) / 2
        logoView.frame.origin.y = 18

        // Add the logo view to the navigation controller.
        self.navigationController?.view.addSubview(logoView)

        // Bring the logo view to the front.
        self.navigationController?.view.bringSubviewToFront(logoView)
        map.delegate = self
        
        // Do any additional setup after loading the view, typically from a nib.
        map.showsUserLocation = true
        map.userTrackingMode = .Follow
        
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()

        // Dispose of any resources that can be recreated.
    }

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

