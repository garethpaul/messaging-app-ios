
import UIKit
import Alamofire
import DigitsKit

class WaitingViewController: UIViewController {
    @IBOutlet var spinner: UIActivityIndicatorView!
    @IBOutlet var waitingText: UIImageView!
    private var isChecking = false
    private var hasMatched = false
    private var isWaitingViewActive = false
    private var waitingViewGeneration = 0
    private var waitingRequest: Request?

    override func viewWillAppear(animated: Bool) {
        super.viewWillAppear(animated)
        isWaitingViewActive = true
        waitingViewGeneration += 1
        check()
    }

    override func viewWillDisappear(animated: Bool) {
        super.viewWillDisappear(animated)
        isWaitingViewActive = false
        waitingViewGeneration += 1
        waitingRequest?.cancel()
        waitingRequest = nil
        finishWaitingCheck()
    }

    @IBAction func refreshBtnClick(sender: AnyObject) {
        check()
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    func check(){
        guard isWaitingViewActive && !isChecking && !hasMatched else {
            return
        }

        isChecking = true
        let checkGeneration = waitingViewGeneration
        self.spinner.hidden = false
        self.waitingText.hidden = true

        let delayTime = dispatch_time(DISPATCH_TIME_NOW,
            Int64(2 * Double(NSEC_PER_SEC)))
        dispatch_after(delayTime, dispatch_get_main_queue()) {
            guard self.isWaitingViewActive && checkGeneration == self.waitingViewGeneration else {
                return
            }

            guard let digitsSession = Digits.sharedInstance().session(),
                let userId = normalizedDigitsUserID(digitsSession.userID) else {
                    self.finishWaitingCheck()
                    return
            }

            let request = Alamofire.request(.POST, getInfo("waitingUrl"), parameters: ["userId": userId, "phoneNumber": digitsSession.phoneNumber])
            self.waitingRequest = request
            request.responseJSON { (req, res, json, error) in
                guard self.waitingRequest === request else {
                    return
                }

                guard self.isWaitingViewActive && checkGeneration == self.waitingViewGeneration else {
                    return
                }

                self.waitingRequest = nil
                self.finishWaitingCheck()
                guard error == nil, let jsonValue = json else {
                    return
                }

                var responseJSON = JSON(jsonValue)
                if responseJSON["match"].string == "True" {
                    // there is now a match
                    self.hasMatched = true
                    self.performSegueWithIdentifier("NavigationViewController", sender: self)
                }
            }
        }
    }

    private func finishWaitingCheck() {
        self.isChecking = false
        self.spinner.hidden = true
        self.waitingText.hidden = false
    }

}
