package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

/**
 * Limit the simulation time.
 * 
 * @author ppinard
 */
public class TimeLimit implements Limit, ActionListener {

    /** Maximum time of a simulation (in milliseconds). */
    private final long maxTime;

    /** Start time of the simulation (in milliseconds). */
    private long startTime;



    /**
     * Creates a new <code>TimeLimit</code>.
     * 
     * @param time
     *            maximum time of a simulation (in seconds)
     */
    public TimeLimit(long time) {
        if (time <= 0)
            throw new IllegalArgumentException(
                    "Maximum simulation time must be greater than 0");
        this.maxTime = time * 1000;
    }



    /**
     * Returns the time limit of a simulation (in seconds).
     * 
     * @return time limit (in seconds)
     */
    public long getMaximumTime() {
        return maxTime / 1000;
    }



    @Override
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) {
        mcss.addActionListener(this);
    }



    @Override
    public void actionPerformed(ActionEvent e) {

        switch (e.getID()) {
        case MonteCarloSS.FirstTrajectoryEvent:
            startTime = System.currentTimeMillis();
            break;

        case MonteCarloSS.TrajectoryEndEvent:

            if (System.currentTimeMillis() - startTime > maxTime)
                ((MonteCarloSS) e.getSource()).requestInterruption();

            break;
        default:
            break;
        }
    }
}
