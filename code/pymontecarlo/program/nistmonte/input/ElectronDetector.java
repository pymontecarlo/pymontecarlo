package pymontecarlo.program.nistmonte.input;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

/**
 * Abstract class of all electron detectors.
 * 
 * @author ppinard
 */
public abstract class ElectronDetector extends AbstractDetector {

    @Override
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) throws EPQException {
        setup(mcss);
    }



    /**
     * Setups the simulation and other listeners. This typically involves adding
     * action listeners to collect data for this detector.
     * 
     * @param mcss
     *            Monte Carlo simulation
     * @throws EPQException
     *             if an error occurs during the setup
     */
    public abstract void setup(MonteCarloSS mcss) throws EPQException;

}
