package pymontecarlo.util;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.Element;
import gov.nist.microanalysis.EPQLibrary.Material;
import gov.nist.microanalysis.EPQLibrary.MaterialFactory;
import gov.nist.microanalysis.EPQLibrary.ToSI;
import gov.nist.microanalysis.NISTMonte.BasicMaterialModel;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.IMaterialScatterModel;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.Region;
import gov.nist.microanalysis.NISTMonte.MultiPlaneShape;
import gov.nist.microanalysis.NISTMonte.PencilBeam;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;
import junittools.test.TestCase;

public class NistMonteTestCase extends TestCase {

    public MonteCarloSS getMonteCarloSS() throws EPQException {
        MonteCarloSS mcss = createMonteCarloSS();

        ElectronGun beam = createElectronGun();
        mcss.setBeamEnergy(beam.getBeamEnergy());
        mcss.setElectronGun(beam);

        createGeometry(mcss.getChamber());

        return mcss;
    }



    public XRayEventListener2 getXRayEventListener(MonteCarloSS mcss)
            throws EPQException {
        double[] pos = getDetectorPosition();
        XRayEventListener2 xrel = new XRayEventListener2(mcss, pos);
        mcss.addActionListener(xrel);
        return xrel;
    }



    public BremsstrahlungEventListener getBremsstrahlungEventListener(
            MonteCarloSS mcss) throws EPQException {
        double[] pos = getDetectorPosition();
        BremsstrahlungEventListener bel =
                new BremsstrahlungEventListener(mcss, pos);
        mcss.addActionListener(bel);
        return bel;
    }



    protected MonteCarloSS createMonteCarloSS() {
        return new MonteCarloSS();
    }



    protected ElectronGun createElectronGun() {
        PencilBeam beam = new PencilBeam();

        beam.setBeamEnergy(getBeamEnergy());
        beam.setCenter(new double[] { 0.0, 0.0,
                0.99 * MonteCarloSS.ChamberRadius });
        beam.setDirection(new double[] { 0.0, 0.0, 1.0 });

        return beam;
    }



    protected void createGeometry(Region chamber) throws EPQException {
        Material mat = MaterialFactory.createPureElement(Element.Au);
        IMaterialScatterModel model = new BasicMaterialModel(mat);

        double dim = 0.01; // 1 mm
        double[] dims = new double[] { dim, dim, dim };
        double[] pos = new double[] { 0.0, 0.0, -dim / 2.0 };
        MultiPlaneShape shape = MultiPlaneShape.createBlock(dims, pos, 0, 0, 0);

        new Region(chamber, model, shape);
    }



    public double[] getDetectorPosition() {
        return new double[] { 0.07652784, 0.0, 0.06421448 };
    }



    public double getBeamEnergy() {
        return ToSI.eV(15e3);
    }
}
